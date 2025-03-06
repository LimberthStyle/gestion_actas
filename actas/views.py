import json
import os
import re
import tempfile
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Acta, Apelacion, Conductor, Infraccion, Vehiculo
from .forms import ConductorForm, InfraccionForm, LoginForm, ActaForm, ApelarActaForm, RegistroForm, EditUserForm, EditUserPasswordForm
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
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
    apelaciones = Apelacion.objects.all()
    
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
        'apelaciones': apelaciones,
    })

@login_required
def registrar_acta(request):
    if request.method == 'POST':
        form = ActaForm(request.POST)
        if form.is_valid():
            print("Formulario válido")  # Depuración
            acta = form.save(commit=False)
            acta.usuario = request.user
            acta.save()
            print("Acta guardada")  # Depuración
            return redirect('dashboard')
        else:
            print("Formulario no válido")  # Depuración
            print(form.errors)  # Depuración
    else:
        form = ActaForm()
    return render(request, 'templates_actas/registrar_acta.html', {'form': form})

@login_required
def lista_actas(request):
    query = request.GET.get('dni', '')  # Obtener el valor del campo de búsqueda
    actas = Acta.objects.all()

    if query:
        actas = actas.filter(id_infrac__id_driver__dni__icontains=query)  # Filtrar por DNI

    return render(request, 'templates_actas/lista_actas.html', {'actas': actas, 'query': query})


@login_required
def apelar_acta(request, acta_id):
    acta = Acta.objects.get(id=acta_id)

    if request.method == 'POST':
        form = ApelarActaForm(request.POST, request.FILES)
        if form.is_valid():
            apelacion = form.save(commit=False)
            apelacion.acta = acta
            apelacion.save()
            return redirect('dashboard')  # Redirige a la lista de actas

    else:
        form = ApelarActaForm()

    return render(request, 'templates_actas/apelar_acta.html', {'form': form, 'acta': acta})

@login_required
def editar_acta(request, acta_id):
    acta = get_object_or_404(Acta, id=acta_id)
    infracciones = Infraccion.objects.all()

    if request.method == "POST":
        fecha_reg = request.POST.get("fecha_reg")
        estado = request.POST.get("estado")
        id_infrac = request.POST.get("id_infrac")

        try:
            infraccion = Infraccion.objects.get(id=id_infrac)

            # Actualizar el acta
            acta.fecha_reg = fecha_reg
            acta.estado = estado
            acta.id_infrac = infraccion
            acta.save()

            return redirect("dashboard")  # Redirige a la lista de actas

        except Infraccion.DoesNotExist:
            return render(request, "templates_actas/editar_acta.html", {"error": "Infracción no encontrada", "acta": acta, "infracciones": infracciones})

    return render(request, "templates_actas/editar_acta.html", {"acta": acta, "infracciones": infracciones})

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
        id_driver = request.POST.get("id_driver")  # Nombre correcto
        id_vehiculo = request.POST.get("id_vehiculo")  # Nombre correcto

        print(f"Fecha: {fecha}")  # Depuración
        print(f"Retención: {retencion}")  # Depuración
        print(f"ID Conductor: {id_driver}")  # Depuración
        print(f"ID Vehículo: {id_vehiculo}")  # Depuración

        try:
            conductor = Conductor.objects.get(id=id_driver)  # Obtener el conductor
            vehiculo = Vehiculo.objects.get(id=id_vehiculo)  # Obtener el vehículo

            # Crear la infracción con los nombres de campos correctos
            Infraccion.objects.create(
                fecha_infrac=fecha,
                retencion=retencion,
                id_driver=conductor,  # Nombre correcto
                id_vehiculo=vehiculo  # Nombre correcto
            )
            return redirect("dashboard")  # Redirige a la lista de infracciones

        except Conductor.DoesNotExist:
            print("Conductor no encontrado")  # Depuración
            return render(request, "templates_infraccion/insertar_infraccion.html", {"error": "Conductor no encontrado"})

        except Vehiculo.DoesNotExist:
            print("Vehículo no encontrado")  # Depuración
            return render(request, "templates_infraccion/insertar_infraccion.html", {"error": "Vehículo no encontrado"})

    conductores = Conductor.objects.all()  # Obtener lista de conductores
    vehiculos = Vehiculo.objects.all()  # Obtener lista de vehículos

    return render(request, "templates_infraccion/insertar_infraccion.html", {"conductores": conductores, "vehiculos": vehiculos})

def editar_infraccion(request, infraccion_id):
    # Obtener la infracción que se va a editar
    infraccion = get_object_or_404(Infraccion, id=infraccion_id)
    
    # Obtener la lista de conductores y vehículos
    conductores = Conductor.objects.all()
    vehiculos = Vehiculo.objects.all()

    if request.method == "POST":
        # Procesar el formulario enviado
        fecha = request.POST.get("fecha_infrac")
        retencion = request.POST.get("retencion")
        id_driver = request.POST.get("id_driver")
        id_vehiculo = request.POST.get("id_vehiculo")

        try:
            # Obtener el conductor y el vehículo seleccionados
            conductor = Conductor.objects.get(id=id_driver)
            vehiculo = Vehiculo.objects.get(id=id_vehiculo)

            # Actualizar la infracción
            infraccion.fecha_infrac = fecha
            infraccion.retencion = retencion
            infraccion.id_driver = conductor
            infraccion.id_vehiculo = vehiculo
            infraccion.save()

            return redirect("dashboard")  # Redirige a la lista de infracciones

        except Conductor.DoesNotExist:
            return render(request, "templates_infraccion/editar_infraccion.html", {"error": "Conductor no encontrado", "infraccion": infraccion, "conductores": conductores, "vehiculos": vehiculos})

        except Vehiculo.DoesNotExist:
            return render(request, "templates_infraccion/editar_infraccion.html", {"error": "Vehículo no encontrado", "infraccion": infraccion, "conductores": conductores, "vehiculos": vehiculos})

    # Si es una solicitud GET, mostrar el formulario con los datos actuales
    return render(request, "templates_infraccion/editar_infraccion.html", {"infraccion": infraccion, "conductores": conductores, "vehiculos": vehiculos})

def eliminar_infraccion(request, id):
    infraccion = get_object_or_404(Infraccion, id=id)
    if request.method == "POST":
        infraccion.delete()
        return redirect('dashboard')
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
            return redirect('dashboard')  # Redirigir a la lista de conductores
    else:
        form = ConductorForm(instance=conductor)
    
    return render(request, 'templates_drivers/editar_conductor.html', {'form': form, 'conductor': conductor})

def eliminar_conductor(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)
    if request.method == 'POST':
        conductor.delete()
        return redirect('dashboard')  # Redirigir a la lista de conductores
    
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
        return redirect("dashboard")

    return render(request, "templates_vehiculo/registrar_vehiculo.html")

def listar_vehiculo(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'templates_vehiculo/listar_vehiculo.html', {'vehiculos': vehiculos})

def editar_vehiculo(request, id):
    vehiculo = get_object_or_404(Vehiculo, id=id)

    if request.method == "POST":
        vehiculo.placa = request.POST.get("placa")
        vehiculo.save()
        return redirect("dashboard")

    return render(request, "templates_vehiculo/editar_vehiculo.html", {"vehiculo": vehiculo})

def eliminar_vehiculo(request, id):
    vehiculo = get_object_or_404(Vehiculo, id=id)
    if request.method == "POST":
        vehiculo.delete()
        return redirect('dashboard')
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
#------------Apelacion-----------------------------------------
def lista_apelacion(request):
    apelaciones = Apelacion.objects.all()
    return render(request, 'apelaciones.html', {'apelaciones': apelaciones})

####--------------reports----------########################
def reporte_actas_pagadas(request):
    # Filtrar solo los conductores con actas pagadas
    actas_pagadas = Acta.objects.filter(estado='Pagado')
    total_conductores = actas_pagadas.count()

    # Crear respuesta en PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Actas_pagadas.pdf"'

    # Crear el PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # -------------- AGREGAR LOGO --------------
    logo_path = os.path.join(os.getcwd(), "actas/static/images/DRTC_LOGO.png")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        p.drawImage(logo, 10, height - 50, width=100, height=40, preserveAspectRatio=True, mask='auto')

    # -------------- TÍTULO --------------
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 50, "Reporte de Actas pagadas")

    # -------------- ENCABEZADOS DE TABLA --------------
    p.setFont("Helvetica-Bold", 10)
    y_position = height - 100

    headers = ["DNI", "Nombre Completo", "Licencia", "Placa", "Propietario", "Fecha Infracción", "Estado"]
    x_positions = [40, 110, 250, 300, 350, 450, 550]  # Ajuste para mostrar "Estado"

    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y_position, header)

    # Línea divisoria
    p.line(30, y_position - 5, width - 30, y_position - 5)

    # -------------- DATOS DE CONDUCTORES --------------
    p.setFont("Helvetica", 9)
    y_position -= 20

    for acta in actas_pagadas:
        conductor = acta.id_infrac.id_driver
        vehiculo = acta.id_infrac.id_vehiculo

        p.drawString(x_positions[0], y_position, conductor.dni)
        p.drawString(x_positions[1], y_position, f"{conductor.nombres} {conductor.apellidos}")
        p.drawString(x_positions[2], y_position, conductor.cat_licen)
        p.drawString(x_positions[3], y_position, vehiculo.placa if vehiculo else "N/A")
        p.drawString(x_positions[4], y_position, acta.propietario[:15])  # Reducimos el texto largo
        p.drawString(x_positions[5], y_position, acta.id_infrac.fecha_infrac.strftime("%d-%m-%Y %H:%M"))
        p.drawString(x_positions[6], y_position, acta.estado)  # ✅ Ahora el Estado se muestra bien

        y_position -= 20  # Espacio entre filas
        if y_position < 50:  # Salto de página si es necesario
            p.showPage()
            y_position = height - 50

    # -------------- TOTAL DE CONDUCTORES PAGADOS --------------
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y_position - 30, f"Total de Actas Pagadas: {total_conductores}")

    # Guardar el PDF
    p.showPage()
    p.save()
    return response

def reporte_actas_no_pagadas(request):
    # Filtrar solo los conductores con actas pagadas
    actas_pagadas = Acta.objects.filter(Q(estado="No Pagado") | Q(estado="no_pagado"))
    total_conductores = actas_pagadas.count()

    # Crear respuesta en PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Actas_no_pagadas.pdf"'

    # Crear el PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # -------------- AGREGAR LOGO --------------
    logo_path = os.path.join(os.getcwd(), "actas/static/images/DRTC_LOGO.png")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        p.drawImage(logo, 10, height - 50, width=100, height=40, preserveAspectRatio=True, mask='auto')

    # -------------- TÍTULO --------------
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 50, "Reporte de Actas No Pagadas")

    # -------------- ENCABEZADOS DE TABLA --------------
    p.setFont("Helvetica-Bold", 10)
    y_position = height - 100

    headers = ["DNI", "Nombre Completo", "Licencia", "Placa", "Propietario", "Fecha Infracción", "Estado"]
    x_positions = [40, 110, 250, 300, 350, 450, 550]  # Ajuste para mostrar "Estado"

    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y_position, header)

    # Línea divisoria
    p.line(30, y_position - 5, width - 30, y_position - 5)

    # -------------- DATOS DE CONDUCTORES --------------
    p.setFont("Helvetica", 9)
    y_position -= 20

    for acta in actas_pagadas:
        conductor = acta.id_infrac.id_driver
        vehiculo = acta.id_infrac.id_vehiculo

        p.drawString(x_positions[0], y_position, conductor.dni)
        p.drawString(x_positions[1], y_position, f"{conductor.nombres} {conductor.apellidos}")
        p.drawString(x_positions[2], y_position, conductor.cat_licen)
        p.drawString(x_positions[3], y_position, vehiculo.placa if vehiculo else "N/A")
        p.drawString(x_positions[4], y_position, acta.propietario[:15])  # Reducimos el texto largo
        p.drawString(x_positions[5], y_position, acta.id_infrac.fecha_infrac.strftime("%d-%m-%Y %H:%M"))
        p.drawString(x_positions[6], y_position, acta.estado)  # ✅ Ahora el Estado se muestra bien

        y_position -= 20  # Espacio entre filas
        if y_position < 50:  # Salto de página si es necesario
            p.showPage()
            y_position = height - 50

    # -------------- TOTAL DE CONDUCTORES PAGADOS --------------
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y_position - 30, f"Total de Actas No Pagadas: {total_conductores}")

    # Guardar el PDF
    p.showPage()
    p.save()
    return response
########################APELACIONES########################
def reporte_actas_apeladas(request):
    # Crear respuesta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_actas_apeladas.pdf"'

    # Crear el canvas de ReportLab
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Agregar logo si existe
    logo_path = os.path.join(os.getcwd(), "actas/static/images/DRTC_LOGO.png")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, 10, height - 50, width=100, height=40, preserveAspectRatio=True, mask='auto')

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, "Reporte de Actas Apeladas")

    # Encabezados de tabla
    c.setFont("Helvetica-Bold", 10)
    headers = ["DNI", "Nombre Completo", "Retención", "Fecha Reg.", "Estado Apelación"]
    x_positions = [50, 120, 250, 350, 450]
    
    for i, header in enumerate(headers):
        c.drawString(x_positions[i], height - 100, header)

    c.line(50, height - 105, 550, height - 105)

    # Obtener actas apeladas
    actas_apeladas = Acta.objects.exclude(estado_apelacion="-")
    total_apeladas = actas_apeladas.count()

    # Agregar datos a la tabla
    y_position = height - 120
    c.setFont("Helvetica", 9)

    for acta in actas_apeladas:
        conductor = acta.id_infrac.id_driver
        datos = [
            conductor.dni,
            f"{conductor.nombres} {conductor.apellidos}",
            acta.id_infrac.retencion,
            acta.fecha_reg.strftime("%d-%m-%Y"),
            acta.estado_apelacion
        ]

        for i, dato in enumerate(datos):
            c.drawString(x_positions[i], y_position, str(dato))

        y_position -= 15
        if y_position < 50:
            c.showPage()
            y_position = height - 100

    # Total de actas apeladas
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position - 20, f"Total de Actas Apeladas: {total_apeladas}")

    # Guardar y retornar PDF
    c.save()
    return response