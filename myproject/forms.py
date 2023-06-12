from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)