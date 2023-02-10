from django.shortcuts import render
from django.http import HttpResponse
from .forms import TestForm 
from app.functions import *
from django.core.files.storage import default_storage
from decouple import config

# Create your views here.

def index(request):
    if request.method == 'POST':  
        form = TestForm(request.POST, request.FILES)  
        if form.is_valid():   
            singer_name = form.cleaned_data.get("singer_name") + " songs"
            number_of_videos = form.cleaned_data.get("number_of_videos")
            audio_duration_in_seconds = form.cleaned_data.get("audio_duration_in_seconds")
            email = form.cleaned_data.get("email")
            video_urls = search_videos(singer_name, number_of_videos, 50, 'short', config('YOUTUBE_API_KEY'))
            if not video_urls:
                print("No video URLs found")
                return
            download_videos(video_urls, audio_duration_in_seconds)
            audio_files = [f"static/app/audio_{i+1}.mp3" for i in range(len(video_urls))]
            merge_audio_files(audio_files, f"output.mp3")
            create_zip_file('static/app/output.mp3', 'static/app/output.zip')
            default_storage.delete('static/app/output.mp3')
            send_email(email)
            default_storage.delete('static/app/output.zip')
        else:
            print(form.errors)
        return render(request,"app/index.html",{'form':form})
    form = TestForm() 
    return render(request,"app/index.html",{'form':form})  