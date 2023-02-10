from django import forms

class TestForm(forms.Form):
    singer_name = forms.CharField(label="Singer Name", widget=forms.TextInput(attrs={'placeholder': 'Sharry Maan', 'class': 'form-control'})) 
    number_of_videos = forms.IntegerField(label="Number of Videos", widget=forms.NumberInput(attrs={'placeholder': '20', 'class': 'form-control'}))
    audio_duration_in_seconds = forms.IntegerField(label="Duration of Each Video", widget=forms.NumberInput(attrs={'placeholder': '30', 'class': 'form-control'}))
    email = forms.EmailField(label="Email Id", widget=forms.TextInput(attrs={'placeholder': 'rohan7grover@gmail.com', 'class': 'form-control'}))

    def clean_number_of_videos(self):
        number_of_videos = self.cleaned_data.get("number_of_videos")
        if number_of_videos < 10:
            raise forms.ValidationError("Number of Videos to be downloaded should be greater than 10")
        return number_of_videos

    def clean_audio_duration_in_seconds(self):
        audio_duration_in_seconds = self.cleaned_data.get("audio_duration_in_seconds")
        if audio_duration_in_seconds < 10:
            raise forms.ValidationError("The duration of each video should be greater than 20 seconds")
        return audio_duration_in_seconds