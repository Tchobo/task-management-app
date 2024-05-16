from django.core.mail import send_mail
import random
from django.conf import settings
from core.models import User
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

def send_opt_via_mail(email):
    user_obj = User.objects.get(email=email)

    opt = random.randint(1000, 9999)
    subject = f"Votre code de confirmation d'adresse mail tast-management est {opt}"
    
    ctx = {
        'username': user_obj.name,
        'codeVerif': opt,
    }
    message=get_template('verify_email.html').render(ctx)
 

    email_from = settings.EMAIL_HOST_USER
    msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
    msg.content_subtype ="html"# Main content is now text/html
   
    try:
        result = msg.send()
       
        user_obj.code_activation = opt

   
        user_obj.save()
    except Exception as e:
        print("Email sending failed:", e)

  
  
    