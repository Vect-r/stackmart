from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


class MailSender():
    stores={'passwordReset':{'path':'dashboard/mails/password_reset.html','subject':'Reset Your Stackmart Credentials'},
            'passwordResetSuccess':{'path':'dashboard/mails/password_reset_success.html','subject':'Security Alert: Password Changed'},
            'mail':{'path':'dashboard/mails/account_verification.html','subject':'Stackmart: Verify Your Identity'}}
    
    def sendMailVerification(self,user,tokenId,request):
        domain = get_current_site(request).domain
        verification_url = f"http://{domain}/verify-mail/{tokenId}/"
        html_message = render_to_string(self.stores['mail']['path'], {
             'user': user,
             'verification_url': verification_url,
             })
        
        plain_message = strip_tags(html_message)

    # 3. Send
        send_mail(
            self.stores['mail']['subject'],
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
         

    def sendPasswordReset(self,request,tokenId,getUser,email):
        domain = get_current_site(request).domain
        reset_url = f"http://{domain}/reset-password/{tokenId}/"
        html_message = render_to_string(self.stores['passwordReset']['path'], {
                'user': getUser,
                'reset_url': reset_url,
            })
                    
        # 2. Create a plain text version (for email clients that disable HTML)
        plain_message = strip_tags(html_message)
                    
        # 3. Send
        send_mail(self.stores['passwordReset']['subject'],
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
                fail_silently=False,
                )
        
    def sendPasswordResetSuccess(self,getUser):
            html_message = render_to_string(self.stores['passwordResetSuccess']['path'], {
                'user': getUser,
            })
            plain_message = strip_tags(html_message)

        # 3. Send the notification
            send_mail(
                self.stores['passwordResetSuccess']['subject'],
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [getUser.email],
                html_message=html_message,
                fail_silently=True, # Don't crash the user flow if mail fails
            )