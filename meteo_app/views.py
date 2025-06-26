from django.shortcuts import render, redirect
import requests
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})



# def login_view(request):
#     return render(request, 'login.html')

# def register(request):
#     return render(request, 'register.html')

@login_required
def meteo(request):
    data = None
    if request.method == 'POST':
        city = request.POST['city']
        
        from decouple import config
        api_key = config('OPENWEATHER_API_KEY')
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
    return render(request, 'meteo.html', {'data': data})

@login_required
def stats(request):
    return render(request, 'stats.html')

