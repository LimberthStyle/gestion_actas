from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Acta, Conductor, Infraccion, Vehiculo
from .forms import LoginForm, ActaForm, ApelarActaForm, RegistroForm, EditUserForm, EditUserPasswordForm
from django.db.models import Q
from django.utils import timezone
from datetime import datetime

#BASE------------------------------------------
def inicio(request):
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# INICIAR SESION----------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'login.html')

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después del registro
            return redirect('login')  # Redirige al dashboard después del registro
    else:
        form = RegistroForm()
    return render(request, 'templates_users/registro_usuario.html', {'form': form})

# INTERFAZ DE INICIO----------------------------------------------
@login_required
def dashboard(request):
    actas = Acta.objects.all()  # Obtén todas las actas
    conductores = Conductor.objects.all()  # Obtén todos los conductores
    return render(request, 'dashboard.html', {
        'actas': actas,
        'conductores': conductores,
    })

@login_required
def registrar_acta(request):
    if request.method == 'POST':
        form = ActaForm(request.POST)
        if form.is_valid():
            acta = form.save(commit=False)
            acta.usuario = request.user
            acta.save()
            return redirect('lista_actas')
    else:
        form = ActaForm()
    return render(request, 'templates_actas/registrar_acta.html', {'form': form})

@login_required
def lista_actas(request):
    query = request.GET.get('q', '')
    actas = Acta.objects.filter(
        Q(id__icontains=query) |
        Q(id_infrac__id_driver__dni__icontains=query) |
        Q(id_infrac__id_driver__nombres__icontains=query) |
        Q(id_infrac__id_driver__apellidos__icontains=query)
    ) if query else Acta.objects.all()
    return render(request, 'templates_actas/lista_actas.html', {'actas': actas})

@login_required
def apelar_acta(request, acta_id):
    acta = get_object_or_404(Acta, id=acta_id)
    if request.method == 'POST':
        form = ApelarActaForm(request.POST, request.FILES)
        if form.is_valid():
            apelacion = form.save(commit=False)
            apelacion.acta = acta
            apelacion.save()
            acta.estado = 'en_proceso'
            acta.save()
            return redirect('lista_actas')
    else:
        form = ApelarActaForm()
    return render(request, 'templates_actas/apelar_acta.html', {'form': form, 'acta': acta})

@login_required
def editar_acta(request, acta_id):
    acta = get_object_or_404(Acta, id=acta_id)
    if request.method == 'POST':
        form = ActaForm(request.POST, instance=acta)
        if form.is_valid():
            form.save()
            return redirect('lista_actas')
    else:
        form = ActaForm(instance=acta)
    return render(request, 'editar_acta.html', {'form': form})

@login_required
def eliminar_acta(request, acta_id):
    acta = get_object_or_404(Acta, id=acta_id)
    acta.delete()
    return redirect('lista_actas')

def insertar_infraccion(request):
    if request.method == 'POST':
        fecha_infrac = request.POST.get('fecha_infrac')
        try:
            fecha_infrac = datetime.strptime(fecha_infrac, '%Y-%m-%dT%H:%M')
        except ValueError:
            return render(request, 'insertar_infraccion.html', {
                'error': 'Formato de fecha incorrecto. Use el selector de fecha y hora.'
            })
            
        retencion = request.POST.get('retencion')
        id_driver_id = request.POST.get('id_driver_id')
        id_vehiculo_id = request.POST.get('id_vehiculo_id')

        try:
            conductor = Conductor.objects.get(id=id_driver_id)
            vehiculo = Vehiculo.objects.get(id=id_vehiculo_id)
            nueva_infraccion = Infraccion(
                fecha_infrac=fecha_infrac,
                retencion=retencion,
                id_driver=conductor,
                id_vehiculo=vehiculo
            )
            nueva_infraccion.save()
            return redirect('dashboard')
        except Conductor.DoesNotExist:
            return render(request, 'insertar_infraccion.html', {
                'error': 'El ID del conductor no existe.'
            })
        except Vehiculo.DoesNotExist:
            return render(request, 'insertar_infraccion.html', {
                'error': 'El ID del vehículo no existe.'
            })

    return render(request, 'templates_infraccion/insertar_infraccion.html')
#-------------------CONDUCTORES--------------
def registrar_conductor(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        cat_licen = request.POST.get('cat_licen')

        nuevo_conductor = Conductor(dni=dni, nombres=nombres, apellidos=apellidos, cat_licen=cat_licen)
        nuevo_conductor.save()
        return redirect('dashboard')

    return render(request, 'templates_drivers/registrar_conductor.html')
def listar_conductor(request):
    conductores = Conductor.objects.all()
    return render(request, 'templates_drivers/listar_conductor.html',{'conductores': conductores})
#----------------Vehiculos--------------------------------------------------------
def registrar_vehiculo(request):
    if request.method == 'POST':
        placa = request.POST.get('placa')

        nuevo_vehiculo = Vehiculo(placa=placa)
        nuevo_vehiculo.save()
        return redirect('dashboard')

    return render(request, 'templates_vehiculo/registrar_vehiculo.html')

#vista para editar usuario
@login_required
def edit_user(request):
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        password_form = EditUserPasswordForm(request.user, request.POST)
        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            password_form.save()
            # Actualizar la sesión con la nueva contraseña (si se cambia)
            update_session_auth_hash(request, request.user)
            return redirect('dashboard')  # Redirigir a donde desees después de la edición
    else:
        user_form = EditUserForm(instance=request.user)
        password_form = EditUserPasswordForm(request.user)
    return render(request, 'templates_users/edit_user.html', {
        'user_form': user_form,
        'password_form': password_form
    })