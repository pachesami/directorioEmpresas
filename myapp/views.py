# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Empresa
from .forms import DjangoUserSignupForm

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
                print(f"Error de integridad: {e}")
                messages.error(request, 'Error al guardar el usuario.')
        else:
            print(f"Errores del formulario: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DjangoUserSignupForm()
    
    return render(request, 'signup.html', {'form': form})

@login_required(login_url='login')
def home(request):
    # Crear empresa
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
    
    # Buscar empresas
    q = request.GET.get('q', '').strip()
    search_field = request.GET.get('field', 'all')  # Campo de búsqueda
    
    empresas_qs = Empresa.objects.all()
    
    if q:
        # Búsqueda según el campo seleccionado
        if search_field == 'compania':
            empresas_qs = empresas_qs.filter(compania__icontains=q)
        elif search_field == 'cliente':
            empresas_qs = empresas_qs.filter(cliente__icontains=q)
        elif search_field == 'codigo':
            empresas_qs = empresas_qs.filter(codigo__icontains=q)
        elif search_field == 'correo':
            empresas_qs = empresas_qs.filter(correo__icontains=q)
        elif search_field == 'telefono':
            empresas_qs = empresas_qs.filter(telefono__icontains=q)
        elif search_field == 'pais':
            empresas_qs = empresas_qs.filter(pais__icontains=q)
        else:
            # Búsqueda en todos los campos (por defecto)
            empresas_qs = empresas_qs.filter(
                Q(compania__icontains=q) | Q(cliente__icontains=q) | Q(codigo__icontains=q) |
                Q(correo__icontains=q)   | Q(pais__icontains=q)    | Q(telefono__icontains=q)
            )
    
    empresas_qs = empresas_qs.order_by('-id')
    
    # Paginación
    paginator = Paginator(empresas_qs, 12)
    page = request.GET.get('page')
    empresas = paginator.get_page(page)
    
    # Determinar si es administrador
    is_admin = request.user.is_staff or request.user.has_perm('myapp.change_empresa')

    return render(request, 'home.html', {
        'empresas': empresas,
        'q': q,
        'search_field': search_field,
        'is_admin': is_admin
    })

@login_required(login_url='login')
def editar_empresa(request, id):
    if not request.user.has_perm('myapp.change_empresa'):
        messages.error(request, 'No tienes permiso para editar empresas.')
        return redirect('home')
    
    empresa = get_object_or_404(Empresa, id=id)
    
    if request.method == 'POST':
        empresa.cliente = request.POST.get('cliente', empresa.cliente)
        empresa.compania = request.POST.get('compania', empresa.compania)
        empresa.telefono = request.POST.get('telefono', empresa.telefono)
        empresa.correo = request.POST.get('correo', empresa.correo)
        empresa.pais = request.POST.get('pais', empresa.pais)
        
        if request.FILES.get('logo'):
            empresa.logo = request.FILES.get('logo')
        
        empresa.save()
        messages.success(request, f'Empresa "{empresa.compania}" actualizada exitosamente.')
        return redirect('home')
    
    return redirect('home')

@login_required(login_url='login')
def eliminar_empresa(request, id):
    if not request.user.has_perm('myapp.delete_empresa'):
        messages.error(request, 'No tienes permiso para eliminar empresas.')
        return redirect('home')
    
    empresa = get_object_or_404(Empresa, id=id)
    
    if request.method == 'POST':
        confirmacion = request.POST.get('confirmacion', '').strip()
        if confirmacion.lower() == 'eliminar':
            nombre_empresa = empresa.compania
            empresa.delete()
            messages.success(request, f'Empresa "{nombre_empresa}" eliminada exitosamente.')
        else:
            messages.error(request, 'Debes escribir "eliminar" para confirmar la acción.')
    
    return redirect('home')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')
