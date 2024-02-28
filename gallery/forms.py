from django import forms


class PictrueLoadingForm(forms.Form):
    description = forms.CharField()
    tags = forms.CharField()
    picture = forms.FileField()


class SigninForm(forms.Form):
    fullname = forms.CharField(min_length=3, max_length=250)
    username = forms.CharField(min_length=8, max_length=16)
    email = forms.EmailField()
    password = forms.CharField(min_length=8, max_length=24)


class AuthForm(forms.Form):
    username = forms.CharField(min_length=8, max_length=16)
    password = forms.CharField(min_length=8, max_length=24)