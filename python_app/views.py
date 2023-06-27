from datetime import datetime
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .models import Product
from django.contrib import messages


def index(request):
    now = datetime.now()
    return render(request, 'index.html')


def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        precio = request.POST['precio']
        cantidad = request.POST['cantidad']
        print(nombre, precio, cantidad)

        try:
            product = Product(nombre=nombre, precio=precio,
                              cantidad_stock=cantidad)
            product.save()
            messages.success(
                request, 'El producto se ha agregado exitosamente.')
        except IntegrityError:
            messages.error(request, 'Ya existe un producto con ese nombre.')

        products = Product.objects.all()
        return render(request, 'lista_productos.html', {'products': products})

    return render(request, 'lista_productos.html')


def buscar_producto(request):
    if request.method == 'GET':
        nombre = request.GET.get('nombre')
        products = Product.objects.filter(nombre__icontains=nombre)
        return render(request, 'lista_productos.html', {'products': products})


def eliminar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')

        if nombre:
            Product.objects.filter(nombre=nombre).delete()
            messages.success(
                request, 'El producto se ha eliminado exitosamente.')
        else:
            messages.error(
                request, 'No se ha proporcionado un nombre de producto válido.')

        return redirect('python_app:lista_productos')


def lista_productos(request):
    products = Product.objects.all()
    return render(request, 'lista_productos.html', {'products': products})
