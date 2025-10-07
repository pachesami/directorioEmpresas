from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Empresa


def signip (request):
    return render(request, 'signip.html')

def signup (request):
    return render(request, 'signup.html')

def home (request):
    if request.method == 'POST':
        Empresa.objects.create(
            cliente=request.POST.get('cliente'),
            compania=request.POST.get('compania'),
            logo=request.FILES.get('logo'),
            telefono=request.POST.get('telefono'),
            correo=request.POST.get('correo'),
            pais=request.POST.get('pais') ,
        )
        
        messages.success(request, 'Empresa registrada exitosamente')
        return redirect('home')
    return render(request, 'home.html')




