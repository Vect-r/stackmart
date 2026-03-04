from django import forms
from .models import Message


class SendMessageForm(forms.ModelForm):
    # class Meta:
    #     model = Message
    #     fields = ['body']
    #     widgets = {
    #         'body':forms.TextInput(attrs={'class':"w-full bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-500 max-h-32",
    #                                          'placeholder':'Type a message...',
    #                                          'maxlength':'300',
    #                                          }),
    #     }
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                # CHANGED: 'leading-relaxed' is now 'leading-normal'
                'class': 'w-full bg-transparent border-0 p-0 m-0 outline-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-500 max-h-32 resize-none custom-scrollbar leading-normal',
                'rows': '1',
                'placeholder': 'Type a message...'
            })
        }