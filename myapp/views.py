from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Empresa
from django.db.models import Q


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
    
    q = request.GET.get('q', '').strip()

    empresas = Empresa.objects.all()
    if q:
        empresas = empresas.filter(
            Q(compania__icontains=q) |
            Q(cliente__icontains=q)  |
            Q(codigo__icontains=q)   |
            Q(correo__icontains=q)   |
            Q(pais__icontains=q)     |
            Q(telefono__icontains=q)
        )

    empresas = empresas.order_by('id')  

    return render(request, 'home.html', {
        'empresas': empresas,
        'q': q,  
    })



