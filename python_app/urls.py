from django.urls import path
from . import views

app_name = 'python_app' # Nombre

urlpatterns = [ # Funcion para mapear todos los url de la app
    path('', views.index, name='index'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('eliminar_producto/', views.eliminar_producto, name='eliminar_producto'),
    path('lista_productos/', views.lista_productos, name='lista_productos'),
]