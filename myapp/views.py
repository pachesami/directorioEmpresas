# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Empresa

# Vista de Login
def login_view(request):
    """Vista para iniciar sesión"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Bienvenido {user.username}!')
            return redirect('home')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos.')
            return render(request, 'signip.html')
    
    return render(request, 'signip.html')


# Vista de Logout
@login_required(login_url='login')
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, '✅ Sesión cerrada correctamente.')
    return redirect('login')


# Vista de Signup (solo admin)
@login_required(login_url='login')
def signup(request):
    """Solo administradores pueden acceder"""
    # ✅ CORRECCIÓN: Verificar permisos o superusuario
    is_admin = request.user.is_superuser or request.user.has_perm('myapp.add_empresa')
    
    if not is_admin:
        messages.error(request, '❌ No tienes permiso para registrar usuarios. Solo administradores.')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validaciones
        if password != confirm_password:
            messages.error(request, '❌ Las contraseñas no coinciden.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ El nombre de usuario ya existe.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ El correo electrónico ya está registrado.')
            return render(request, 'signup.html')
        
        try:
            # Crear usuario
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = True
            user.save()
            
            messages.success(request, f'✅ Usuario "{username}" registrado exitosamente.')
            return redirect('home')
        
        except Exception as e:
            messages.error(request, f'❌ Error al crear usuario: {str(e)}')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')


# Vista de Home
@login_required(login_url='login')
def home(request):
    # ✅ CORRECCIÓN: Verificar permisos individuales O superusuario
    is_admin = (
        request.user.is_superuser or 
        request.user.has_perm('myapp.add_empresa') or
        request.user.has_perm('myapp.change_empresa') or
        request.user.has_perm('myapp.delete_empresa')
    )
    
    # DEBUG: Imprimir permisos del usuario
    print(f"\n{'='*50}")
    print(f"👤 Usuario: {request.user.username}")
    print(f"🔑 Es superusuario: {request.user.is_superuser}")
    print(f"📋 Permisos:")
    print(f"   - add_empresa: {request.user.has_perm('myapp.add_empresa')}")
    print(f"   - change_empresa: {request.user.has_perm('myapp.change_empresa')}")
    print(f"   - delete_empresa: {request.user.has_perm('myapp.delete_empresa')}")
    print(f"🛡️ is_admin: {is_admin}")
    print(f"{'='*50}\n")
    
    q = request.GET.get('q', '').strip()
    search_field = request.GET.get('field', 'all')
    
    # Filtrar empresas
    empresas_list = Empresa.objects.all()
    
    # Aplicar búsqueda
    if q:
        if search_field == 'all':
            empresas_list = empresas_list.filter(
                Q(compania__icontains=q) | 
                Q(cliente__icontains=q) | 
                Q(codigo__icontains=q) |
                Q(correo__icontains=q) |
                Q(telefono__icontains=q) |
                Q(pais__icontains=q)
            )
        elif search_field == 'compania':
            empresas_list = empresas_list.filter(compania__icontains=q)
        elif search_field == 'cliente':
            empresas_list = empresas_list.filter(cliente__icontains=q)
        elif search_field == 'codigo':
            empresas_list = empresas_list.filter(codigo__icontains=q)
        elif search_field == 'correo' and is_admin:
            empresas_list = empresas_list.filter(correo__icontains=q)
        elif search_field == 'telefono' and is_admin:
            empresas_list = empresas_list.filter(telefono__icontains=q)
        elif search_field == 'pais' and is_admin:
            empresas_list = empresas_list.filter(pais__icontains=q)
    
    empresas_list = empresas_list.order_by('-id')
    
    # Paginación
    paginator = Paginator(empresas_list, 12)
    page_number = request.GET.get('page')
    empresas = paginator.get_page(page_number)
    
    # ✅ POST: Agregar empresa
    if request.method == 'POST':
        if not (is_admin and request.user.has_perm('myapp.add_empresa')):
            messages.error(request, '❌ No tienes permiso para agregar empresas.')
            return redirect('home')
        
        cliente = request.POST.get('cliente')
        compania = request.POST.get('compania', '')
        telefono = request.POST.get('telefono', '')
        correo = request.POST.get('correo', '')
        pais = request.POST.get('pais', '')
        logo = request.FILES.get('logo')
        
        if cliente:
            empresa = Empresa.objects.create(
                cliente=cliente,
                compania=compania,
                telefono=telefono,
                correo=correo,
                pais=pais,
                logo=logo
            )
            messages.success(request, f'✅ Empresa "{empresa.compania or empresa.cliente}" agregada correctamente.')
            return redirect('home')
    
    context = {
        'empresas': empresas,
        'is_admin': is_admin,
        'q': q,
        'search_field': search_field,
    }
    return render(request, 'home.html', context)


# ✅ Vista de Editar Empresa (SOLO ADMIN)
@login_required(login_url='login')
def editar_empresa(request, id):
    # ✅ SEGURIDAD: Verificar permiso específico
    if not (request.user.is_superuser or request.user.has_perm('myapp.change_empresa')):
        messages.error(request, '❌ No tienes permiso para editar empresas.')
        return redirect('home')
    
    empresa = get_object_or_404(Empresa, id=id)
    
    if request.method == 'POST':
        empresa.cliente = request.POST.get('cliente')
        empresa.compania = request.POST.get('compania', '')
        empresa.telefono = request.POST.get('telefono', '')
        empresa.correo = request.POST.get('correo', '')
        empresa.pais = request.POST.get('pais', '')
        
        if request.FILES.get('logo'):
            empresa.logo = request.FILES.get('logo')
        
        empresa.save()
        messages.success(request, f'✅ Empresa "{empresa.compania or empresa.cliente}" actualizada.')
        return redirect('home')
    
    return redirect('home')


# ✅ Vista de Eliminar Empresa (SOLO ADMIN)
@login_required(login_url='login')
def eliminar_empresa(request, id):
    # ✅ SEGURIDAD: Verificar permiso específico
    if not (request.user.is_superuser or request.user.has_perm('myapp.delete_empresa')):
        messages.error(request, '❌ No tienes permiso para eliminar empresas.')
        return redirect('home')
    
    empresa = get_object_or_404(Empresa, id=id)
    nombre = empresa.compania or empresa.cliente
    empresa.delete()
    messages.success(request, f'✅ Empresa "{nombre}" eliminada correctamente.')
    return redirect('home')
