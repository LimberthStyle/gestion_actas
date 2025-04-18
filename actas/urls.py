from django.urls import path
from . import views

urlpatterns = [
    #path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_user/', views.edit_user, name='edit_user'),
    #---------------ACTAS-----------------------------------------------
    path('registrar_acta/', views.registrar_acta, name='registrar_acta'),
    path('lista_actas/', views.lista_actas, name='lista_actas'),
    path('apelar_acta/<int:acta_id>/', views.apelar_acta, name='apelar_acta'),
    path('editar_acta/<int:acta_id>/', views.editar_acta, name='editar_acta'),
    path('eliminar_acta/<int:acta_id>/', views.eliminar_acta, name='eliminar_acta'),
    #---------------------------------------------------------------------------------------------------
    path('', views.login_view, name='home'),  # Establecer la vista de inicio de sesión como la raíz
    
    #---------------------------CONDUCTORES---------------------------------------------------------------
    path('listar_conductor/', views.listar_conductor, name='listar_conductor'),
    path('registrar_conductor/', views.registrar_conductor, name='registrar_conductor'),
    path('editar_conductor/<int:conductor_id>/', views.editar_conductor, name='editar_conductor'),
    path('eliminar_conductor/<int:conductor_id>/', views.eliminar_conductor, name='eliminar_conductor'),
    #-----------------------------------VEHICULOS-----------------------------------------------------
    path('listar_vehiculo/', views.listar_vehiculo, name='listar_vehiculo'),
    path('registrar_vehiculo/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path("vehiculos/editar/<int:id>/", views.editar_vehiculo, name="editar_vehiculo"),
    path("vehiculos/eliminar/<int:id>/", views.eliminar_vehiculo, name="eliminar_vehiculo"),
    #-----------------------------------vISTA DASHBOARD-----------------------------------------
    path('dashboard_view/', views.dashboard_view, name='dashboard_view'),
    #-------------------------------INFRACCIONES-------------------------------------
    path('listar_infraccion/', views.listar_infraccion, name='listar_infraccion'),
    path('insertar_infraccion/', views.insertar_infraccion, name='insertar_infraccion'),
    path('editar_infraccion/<int:infraccion_id>/', views.editar_infraccion, name='editar_infraccion'),
    path('eliminar_infraccion/<int:id>/', views.eliminar_infraccion, name='eliminar_infraccion'),
    #-----------------------------Apleacion--------------------------------------------------
    path('lista_apelacion/<int:id>/', views.lista_apelacion, name='lista_apelacion'),
    #-----------------------------------REPORTES---------------------------------------------------
    path('reportes-p/', views.reporte_actas_pagadas, name='reporte_pagados'),
    path('reportes-np/', views.reporte_actas_no_pagadas, name='reportes_no_pagados'),
    path('reportes-ap/', views.reporte_actas_apeladas, name='reporte_actas_apeladas'),
]
