# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Empresa               # <-- Quita ", Usuario"
from .forms import DjangoUserSignupForm   # <-- usa el form basado en auth.User

def signip(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}!')
            return redirect('home')
        messages.error(request, 'Usuario o contraseña incorrecta.')
    return render(request, 'signip.html')

def signup(request):
    if request.method == 'POST':
        form = DjangoUserSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    messages.success(request, 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.')
                    return redirect('login')
            except IntegrityError as e:
                print(f"Error de integridad: {e}")  # Para debugging
                messages.error(request, 'Error al guardar el usuario.')
        else:
            # Imprimir errores para debugging
            print(f"Errores del formulario: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DjangoUserSignupForm()
    
    return render(request, 'signup.html', {'form': form})

@login_required(login_url='login')  # o 'Login'
def home(request):
    if request.method == 'POST':
        if not request.user.has_perm('myapp.add_empresa'):
            messages.error(request, 'No tienes permiso para agregar empresas.')
            return redirect('home')
        Empresa.objects.create(
            cliente=request.POST.get('cliente'),
            compania=request.POST.get('compania'),
            logo=request.FILES.get('logo'),
            telefono=request.POST.get('telefono'),
            correo=request.POST.get('correo'),
            pais=request.POST.get('pais'),
        )
        messages.success(request, 'Empresa registrada exitosamente')
        return redirect('home')

    q = request.GET.get('q', '').strip()
    empresas = Empresa.objects.all()
    if q:
        empresas = empresas.filter(
            Q(compania__icontains=q) | Q(cliente__icontains=q) | Q(codigo__icontains=q) |
            Q(correo__icontains=q)   | Q(pais__icontains=q)    | Q(telefono__icontains=q)
        )
    empresas = empresas.order_by('id')
    return render(request, 'home.html', {'empresas': empresas, 'q': q})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')  # o 'Login'
