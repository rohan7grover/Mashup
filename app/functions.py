from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
import requests
import os
import threading
import traceback
from pydub import AudioSegment
from pytube import YouTube
import zipfile

def search_videos(query, number_of_videos, results_per_page, video_duration, api_key):
    video_urls = []
    next_page_token = None
    max_iterations = 3 # To ensure a responsible usage limit API requests being sent to the YOUTUBE API
    iteration_counter = 0

    while True:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults={results_per_page}&key={api_key}&videoDuration={video_duration}"

        if next_page_token:
            url += f"&pageToken={next_page_token}"

        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print("An error occurred while making the request:", e)
            break

        if response.status_code >= 200 and response.status_code < 300:
            try:
                data = response.json()
            except ValueError as e:
                print("An error occurred while parsing the response:", e)
                break

            for item in data['items']:
                if item['snippet']['liveBroadcastContent'] == 'none':
                    video_urls.append(
                        f"https://www.youtube.com/watch?v={item['id']['videoId']}")

            next_page_token = data.get('nextPageToken')

            if len(video_urls) >= number_of_videos:
                break

            if not next_page_token:
                break

            iteration_counter += 1
            if iteration_counter >= max_iterations:
                break

        else:
            print("Request failed")
            break

    return video_urls[:number_of_videos]


def download_video(url, video_filename, audio_filename, audio_duration_in_seconds):
    try:
        video = YouTube(url)
        stream = video.streams.first()
        print(f"Downloading: {video.title}")
        stream.download(filename=os.path.join("static/app", video_filename))

        audio = AudioSegment.from_file(os.path.join(
            "static/app", video_filename), format="mp4")
        audio = audio[:audio_duration_in_seconds * 1000]
        audio.export(os.path.join("static/app", audio_filename), format="mp3")
        os.remove(os.path.join("static/app", video_filename))
    except Exception as e:
        print(f"Error downloading video from URL: {url}")
        print(f"Error: {e}")
        print(traceback.format_exc())


def download_videos(video_urls, audio_duration_in_seconds):
    threads = []
    for i, url in enumerate(video_urls):
        t = threading.Thread(target=download_video, args=(
            url, f"video_{i+1}.mp4", f"audio_{i+1}.mp3", audio_duration_in_seconds))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def merge_audio_files(audio_files, output_file):
    try:
        audio = AudioSegment.from_file(audio_files[0], format="mp3")
        for audio_file in audio_files[1:]:
            audio = audio + AudioSegment.from_file(audio_file, format="mp3")

        audio.export(os.path.join("static/app", output_file), format="mp3")
        for audio_file in audio_files:
            os.remove(audio_file)
    except Exception as e:
        print(f"Error merging audio files: {audio_files}")
        print(f"Error: {e}")
        print(traceback.format_exc())


def send_email(email):
    mail = EmailMessage(
        'Mashup', 'Hey there! Please find your MASHUP in the attachments', 'settings.EMAIL_HOST_USER', [
            email],
    )
    mail.attach_file('static/app/output.zip')
    mail.send()


def create_zip_file(mp3_file_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        zip_file.write(mp3_file_path, arcname=mp3_file_path.split('/')[-1])