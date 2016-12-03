from base64 import b64encode
from hashlib import sha256
from os import urandom

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from forms import MagicAuthForm
from namubufferi.settings import DEBUG
from magicauth.models import MagicToken

def magic_auth(request, magic_token=None):
    """
    """
    if request.method == 'POST':
        # Validate reCAPTCHA
        # https://developers.google.com/recaptcha/docs/verify
        # http://docs.python-requests.org/en/master/user/quickstart/#more-complicated-post-requests
        # http://docs.python-requests.org/en/master/user/quickstart/#json-response-content
        payload = {"secret": "6LfUqSgTAAAAACc5WOqVLLmJP_3SC3bWp094D0vo",
                   "response": request.POST['g-recaptcha-response']}
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload).json()
        # TODO: Check if we need headers
        if not r['success']:
            print ("reCAPTCHA validation failed.")
            if not DEBUG:
                return JsonResponse({'modalMessage': 'Check yourself you might be a robot. Try again.'})

        # Validate form
        magic_auth_form = MagicAuthForm(request.POST)
        if magic_auth_form.is_valid():
            # Try to find the user or create a new one
            try:
                user = User.objects.get(username=request.POST['aalto_username'])
            except:  # DoesNotExist
                new_user = User.objects.create_user(request.POST['aalto_username'],
                                                    email=request.POST['aalto_username'] + '@aalto.fi',
                                                    password=b64encode(sha256(urandom(56)).digest()))

                new_magic_token = MagicToken()
                new_magic_token.user = new_user
                new_magic_token.save()
                user = new_user

            user.magictoken.update()
            current_site = get_current_site(request)
            magic_link = current_site.domain + reverse('magic', kwargs={'magic_token': user.magictoken.magic_token})

            # Send mail to user
            mail = EmailMultiAlternatives(
                subject="Namubufferi - Login",
                body=("Hello. Authenticate to Namubufferi using this link. It's valid for 15 minutes.\n"
                      + magic_link),
                from_email="<namubufferi@athene.fi>",
                to=[user.email]
            )
            mail.attach_alternative(("<h1>Hello."
                                     "</h1><p>Authenticate to Namubufferi using this link. It's valid for 15 minutes.</p>"
                                     '<a href="http://' + magic_link + '"> Magic Link </a>'
                                     ), "text/html")
            try:
                mail.send()
                print "Mail sent"
            except:
                print "Mail not sent"

            if DEBUG:
                return JsonResponse({'modalMessage': 'Check your email.<br><a href="http://' + magic_link + '"> Magic Link </a>'})
            else:
                return JsonResponse({'modalMessage': 'Check your email.'})
        else:
            return HttpResponse('{"errors":' + magic_auth_form.errors.as_json() + '}', content_type="application/json")

    elif (magic_token):
        user = authenticate(magic_token=magic_token)
        if user:
            login(request, user)
            return redirect('/')
        else:
            return HttpResponse(status=410)
    else:
        return render(request, 'magicauth/base_magiclogin.html', {'magic_auth_form': MagicAuthForm()})