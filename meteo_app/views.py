from django.shortcuts import render, redirect
import requests
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from . import tokens as tk
from django.contrib.auth import get_user_model




# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return redirect('meteo')  # nom de l'URL vers ta page météo
    # sinon, afficher la page d’accueil classique
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # utilisateur désactivé avant validation
            user.save()

            current_site = get_current_site(request)
            subject = 'Activation de votre compte Good Air'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': tk.account_activation_token.make_token(user),
            })
            send_mail(subject, message, 'no-reply@yourdomain.com', [user.email])

            return render(request, 'registration_pending.html')  # page pour dire "verifiez vos emails"
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

from django.contrib.auth import login



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and tk.account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='meteo_app.backend.EmailOrUsernameBackend')
        return redirect('home')
    else:
        return render(request, 'activation_invalid.html')  # token invalide



VALID_CITIES = [
    "paris", "marseille", "lyon", "toulouse", "nice",
    "nantes", "montpellier", "strasbourg", "bordeaux", "lille"
]

@login_required
def meteo(request):
    data = None
    if request.method == 'POST':
        
        
        city = request.POST.get('city', '').lower()
        if city not in VALID_CITIES:
            # tu peux gérer une erreur ou un message utilisateur ici
            # par exemple, afficher un message d'erreur
            messages.error(request, "Ville non valide, merci de choisir dans la liste.")
        else:
            # récupère les données météo normalement
            from decouple import config
            api_key = config('OPENWEATHER_API_KEY')
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
    return render(request, 'meteo.html', {'data': data,
        'current_page': 'meteo',})

@login_required
def stats(request):
    return render(request, 'stats.html', 
        {'current_page': 'stats',})

