from django import forms
from .models import Message


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body':forms.TextInput(attrs={'class':"w-full bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-500 max-h-32",
                                             'placeholder':'Type a message...',
                                             'maxlength':'300',
                                             }),
        }