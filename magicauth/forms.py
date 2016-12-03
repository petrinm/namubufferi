from django import forms
from django.core.validators import RegexValidator

class MagicAuthForm(forms.Form):
    # http://emailregex.com/
    emailregex = RegexValidator(r"(^[a-zA-Z0-9_.+-]*$)", 'Enter a valid email.')

    aalto_username = forms.CharField(label='Username',
                                     validators=[emailregex],
                                     widget=forms.TextInput(attrs={'placeholder': 'teemu.teekkari',
                                                                   'class': 'form-control',
                                                                   }))
