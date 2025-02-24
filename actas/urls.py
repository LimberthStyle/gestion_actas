from django.urls import path
from . import views

urlpatterns = [
    #path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #---------------ACTAS-----------------------------------------------
    path('registrar_acta/', views.registrar_acta, name='registrar_acta'),
    path('lista_actas/', views.lista_actas, name='lista_actas'),
    path('apelar_acta/<int:acta_id>/', views.apelar_acta, name='apelar_acta'),
    path('editar_acta/<int:acta_id>/', views.editar_acta, name='editar_acta'),
    path('eliminar_acta/<int:acta_id>/', views.eliminar_acta, name='eliminar_acta'),
    path('', views.login_view, name='home'),  # Establecer la vista de inicio de sesión como la raíz
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('registrar_conductor/', views.registrar_conductor, name='registrar_conductor'),
    path('registrar_vehiculo/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('insertar_infraccion/', views.insertar_infraccion, name='insertar_infraccion'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('listar_conductor/', views.listar_conductor, name='listar_conductor')
]
