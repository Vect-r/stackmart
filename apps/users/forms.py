from django import forms
from apps.master.utils.inputValidators import validatePassword as strong_password
from apps.master.utils.inputValidators import ValidationError
from apps.master.auth.utils import hash_password
from apps.users.models import Blog

# class PasswordResetForm(forms.Form):
#     password = forms.CharField(max_length=100,widget=forms.PasswordInput(),validators=)
#     confirm_password  = forms.CharField(max_length=100,widget=forms.PasswordInput())


class PasswordResetForm(forms.Form):
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(render_value=True),
        validators=[strong_password],
    )
    confirm_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(render_value=True),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")

        return cleaned_data
    
# class BlogAdd(forms.form):
#     title = forms.CharField(max_length=100)
#     body = forms.Textarea() #Body will be our markdown
#     images = forms.FileField() # only jpg, jpeg, png, webp allowed

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        # You can specify fields explicitly as a list:
        fields = ['title', 'category', 'body', 'summary', "cover_image"]
        # Or include all fields using '__all__':
        # fields = '__all__'

