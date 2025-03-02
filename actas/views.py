import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Acta, Conductor, Infraccion, Vehiculo
from .forms import ConductorForm, InfraccionForm, LoginForm, ActaForm, ApelarActaForm, RegistroForm, EditUserForm, EditUserPasswordForm
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
    # Calcular el total de actas registradas esta semana
    total_actas_registradas = Acta.objects.filter(fecha_reg__week=timezone.now().isocalendar()[1]).count()
    
    # Calcular el total de actas apeladas esta semana
    total_actas_apeladas = Acta.objects.filter(
        fecha_reg__week=timezone.now().isocalendar()[1],
        apelacion__isnull=False  # Filtra actas que tienen una apelación relacionada
    ).count()
    
    # Calcular el porcentaje de infracciones esta semana
    total_infracciones = Infraccion.objects.filter(fecha_infrac__week=timezone.now().isocalendar()[1]).count()
    total_actas = Acta.objects.filter(fecha_reg__week=timezone.now().isocalendar()[1]).count()
    porcentaje_infracciones = (total_infracciones / total_actas) * 100 if total_actas > 0 else 0
    
    # SECCIONES DEL SIDEBAR
    actas = Acta.objects.all()  # Obtén todas las actas
    conductores = Conductor.objects.all()  # Obtén todos los conductores
    vehiculos = Vehiculo.objects.all()
    infractions = Infraccion.objects.all()
    
    return render(request, 'dashboard.html', {
        # MUESTRA ESTADISTICAS
        'total_actas_registradas': total_actas_registradas,
        'total_actas_apeladas': total_actas_apeladas,
        'porcentaje_infracciones': round(porcentaje_infracciones, 2),
        # SECCIONES DEL SIDEBAR
        'actas': actas,
        'conductores': conductores,
        'vehiculos': vehiculos,
        'infractions': infractions,
    })

@login_required
def registrar_acta(request):
    if request.method == 'POST':
        form = ActaForm(request.POST)
        if form.is_valid():
            acta = form.save(commit=False)
            acta.usuario = request.user
            acta.save()
            return redirect('dashboard')
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
#--------------------------INFRACCIONES--------------------------------------
def listar_infraccion(request):
    infractions = Infraccion.objects.all()
    return render(request, 'templates_infraccion/listar_infraccion.html', {'infractions': infractions})

@login_required
def insertar_infraccion(request):
    if request.method == "POST":
        fecha = request.POST.get("fecha_infrac")
        retencion = request.POST.get("retencion")
        conductor_id = request.POST.get("id_driver_id")
        vehiculo_id = request.POST.get("id_vehiculo_id")

        try:
            conductor = Conductor.objects.get(id=conductor_id)
            vehiculo = Vehiculo.objects.get(id=vehiculo_id)

            Infraccion.objects.create(
                fecha_infrac=fecha,
                retencion=retencion,
                conductor=conductor,
                vehiculo=vehiculo
            )
            return redirect("lista_infracciones")  # Redirige a la lista de infracciones

        except Conductor.DoesNotExist or Vehiculo.DoesNotExist:
            return render(request, "insertar_infraccion.html", {"error": "Conductor o vehículo no encontrado"})

    conductores = Conductor.objects.all()  # Obtener lista de conductores
    vehiculos = Vehiculo.objects.all()  # Obtener lista de vehículos

    return render(request, "templates_infraccion/insertar_infraccion.html", {"conductores": conductores, "vehiculos": vehiculos})

def editar_infraccion(request, id):
    infraccion = get_object_or_404(Infraccion, id=id)
    if request.method == "POST":
        form = InfraccionForm(request.POST, instance=infraccion)
        if form.is_valid():
            form.save()
            return redirect('listar_infracciones')
    else:
        form = InfraccionForm(instance=infraccion)
    return render(request, 'templates_infraccion/editar_infraccion.html', {'form': form})

def eliminar_infraccion(request, id):
    infraccion = get_object_or_404(Infraccion, id=id)
    if request.method == "POST":
        infraccion.delete()
        return redirect('listar_infracciones')
    return render(request, 'templates_infraccion/eliminar_infraccion.html', {'infraccion': infraccion})
#-------------------CONDUCTORES--------------
@login_required
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
@login_required
def listar_conductor(request):
    conductores = Conductor.objects.all()
    return render(request, 'templates_drivers/listar_conductor.html',{'conductores': conductores})

def editar_conductor(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)
    if request.method == 'POST':
        form = ConductorForm(request.POST, instance=conductor)
        if form.is_valid():
            form.save()
            return redirect('listar_conductores')  # Redirigir a la lista de conductores
    else:
        form = ConductorForm(instance=conductor)
    
    return render(request, 'templates_drivers/editar_conductor.html', {'form': form, 'conductor': conductor})

def eliminar_conductor(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)
    if request.method == 'POST':
        conductor.delete()
        return redirect('listar_conductores')  # Redirigir a la lista de conductores
    
    return render(request, 'templates_drivers/eliminar_conductor.html', {'conductor': conductor})
#----------------Vehiculos--------------------------------------------------------
@login_required
def registrar_vehiculo(request):
    if request.method == "POST":
        placa = request.POST.get("placa").upper()
        regex = r"^[A-Z][A-Z0-9]*-\d{3}$"  # 1ra letra + letras/números + "-" + 3 números

        if not re.match(regex, placa):
            messages.error(request, "⚠ La placa debe tener el formato correcto (Ej: A23-456)")
            return redirect("registrar_vehiculo")

        if Vehiculo.objects.filter(placa=placa).exists():
            messages.error(request, "⚠ La placa ya está registrada")
            return redirect("registrar_vehiculo")

        Vehiculo.objects.create(placa=placa)
        messages.success(request, "✅ Vehículo registrado exitosamente")
        return redirect("listar_vehiculo")

    return render(request, "templates_vehiculo/registrar_vehiculo.html")

def listar_vehiculo(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'templates_vehiculo/listar_vehiculo.html', {'vehiculos': vehiculos})

def editar_vehiculo(request, id):
    vehiculo = get_object_or_404(Vehiculo, id=id)

    if request.method == "POST":
        vehiculo.placa = request.POST.get("placa")
        vehiculo.save()
        return redirect("lista_vehiculos")

    return render(request, "templates_vehiculo/editar_vehiculo.html", {"vehiculo": vehiculo})

def eliminar_vehiculo(request, id):
    vehiculo = get_object_or_404(Vehiculo, id=id)
    if request.method == "POST":
        vehiculo.delete()
        return redirect('listar_vehiculo')
    return render(request, 'templates_vehiculo/eliminar_vehiculo.html', {'vehiculo': vehiculo})
#---------------------------vista para editar usuario--------------------------------------------
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
#--------------------------------ESTADISTICAS Y REPORTES------------------------

def dashboard_view(request):
  # Calcular el total de actas registradas esta semana
    total_actas_registradas = Acta.objects.filter(fecha_reg__week=timezone.now().isocalendar()[1]).count()
    
    # Calcular el total de actas apeladas esta semana
    total_actas_apeladas = Acta.objects.filter(
        fecha_reg__week=timezone.now().isocalendar()[1],
        apelacion__isnull=False  # Filtra actas que tienen una apelación relacionada
    ).count()
    
    # Calcular el porcentaje de infracciones esta semana
    total_infracciones = Infraccion.objects.filter(fecha_infrac__week=timezone.now().isocalendar()[1]).count()
    total_actas = Acta.objects.filter(fecha_reg__week=timezone.now().isocalendar()[1]).count()
    porcentaje_infracciones = (total_infracciones / total_actas) * 100 if total_actas > 0 else 0

    context = {
        'total_actas_registradas': total_actas_registradas,
        'total_actas_apeladas': total_actas_apeladas,
        'porcentaje_infracciones': round(porcentaje_infracciones, 2),
    }
    return render(request, 'dashboard.html', context)