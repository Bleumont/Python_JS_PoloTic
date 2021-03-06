from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from .decorators import allowed_users, unauthenticated_user, admin_only
from .models import Pedidos, Pacientes, Profesionales, Turnos, Productos
import datetime
from .forms import *

# Create your views here.
def index(request):
    return render(request, 'users/index.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, username)
            redirect('dashboard')
    else:
        return render(request, 'users/login.html', )

def logout_user(request):
    logout(request)
    return redirect('logout')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria','admin','Gerencia'])
def secretaria(request):
    turnos = Turnos.objects.all()
    context = {'turnos': turnos}

    return render(request, 'users/secretaria.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria','admin','Gerencia'])
def add_turno(request):
    
    form = AddTurnoForm(request.POST)
    if request.method == 'POST':
        form = AddTurnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('secretaria')

    return render(request, 'users/add_turno.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria','admin','Gerencia'])
def del_turno(request, t_key):
    turno = Turnos.objects.get(id=t_key)
    
    if request.method == 'POST':
        turno.delete()
        return redirect('secretaria')

    return render(request, 'users/del_turno.html', {'turno': turno})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Taller','admin','Gerencia'])
def taller(request):
    pedidos = Pedidos.objects.all()
    pedidos = pedidos.filter(estado_pedido='Taller')
    finalizados = Pedidos.objects.filter(estado_pedido='Finalizado')
    context = {'Pedidos': pedidos, 'Finalizados': finalizados}

    return render(request, 'users/taller.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Gerencia','admin','Gerencia'])
def gerencia(request):
    today = datetime.date.today()
    pedidos = Pedidos.objects.all()
    pacientes = Pacientes.objects.all()
    medicos = Profesionales.objects.all()
    turnos = Turnos.objects.all()

    asistencias = turnos.filter(asistencia=True).filter(fecha__year=today.year, fecha__month=today.month)
    inasistencias = turnos.filter(asistencia=False).filter(fecha__year=today.year, fecha__month=today.month)
    cantidad_ventas = Pedidos.objects.values('producto').order_by('producto').annotate(vendidos=Sum('cantidad')).filter(estado_pedido='Finalizado', fecha_de_compra__year=today.year, fecha_de_compra__month=today.month)
    
    total_ventas = pedidos.values('vendedor').annotate(vendidos=Sum('cantidad')).filter(estado_pedido='Finalizado').filter(fecha_de_compra__year=today.year, fecha_de_compra__month=today.month)
   
    pedidos_mes = pedidos.filter(fecha_de_compra__year=today.year, fecha_de_compra__month=today.month)
    pacientes_compradores = []
    for pedido in pedidos_mes:
        paciente = Pacientes.objects.get(nombre=pedido.comprador.nombre)
        pacientes_compradores.append(paciente)
    pacientes_set = set(pacientes_compradores)

    context = {'Pedidos': pedidos, 'Pacientes': pacientes, 'Ventas_Totales': total_ventas, 
    'Asistencias': asistencias, 'Inasistencias': inasistencias, 'Clientes':pacientes_set,
    'Turnos': turnos, 'Profesionales': medicos, 'Mas_vendidos':cantidad_ventas}

    return render(request, 'users/gerencia.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Ventas','admin','Gerencia'])
def ventas(request):
    pedidos = Pedidos.objects.all()
    productos = Productos.objects.all()
    form = PedidoForm()
    context = {'Pedidos': pedidos, 'Productos':productos, 'form': form}

    return render(request, 'users/ventas.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Ventas','admin','Gerencia'])
def add_pedido(request):
    
    form = AddPedidoForm(request.POST)

    if request.method == 'POST':
        form = AddPedidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ventas')

    return render(request, 'users/add_pedido.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Ventas','admin','Gerencia'])
def add_producto(request):
    
    form = AddProductoForm(request.POST)

    if request.method == 'POST':
        form = AddProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ventas')

    return render(request, 'users/add_producto.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Profesionales','admin','Gerencia'])
def medicos(request):
    turnos = Turnos.objects.filter(profesional=request.user.username)
    turnos = turnos.order_by('fecha')
    
    fecha = request.GET.get('fecha')
    if fecha != '' and fecha is not None:
        turnos = turnos.filter(fecha__contains=fecha)
    
    context = {'turnos': turnos}

    return render(request, 'users/medicos.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Profesionales','admin','Gerencia'])
def update_paciente(request, p_key):
    turno = Turnos.objects.get(id=p_key)
    paciente = Pacientes.objects.filter(nombre=turno.paciente)[0]
    form = UpdatePacienteForm(instance=paciente)
    context = {'paciente': paciente, 'form': form}
    if request.method == 'POST':
        form = UpdatePacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('medicos')

    return render(request, 'users/update_paciente.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Taller', 'Ventas','admin'])
def update_pedido(request, p_key):
    pedido = Pedidos.objects.get(id=p_key)
    form = UpdatePedidoForm(instance=pedido)
    context = {'pedido': pedido, 'form': form}
    if request.method == 'POST':
        form = UpdatePedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('taller')

    return render(request, 'users/update_pedido.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Ventas','admin', 'Gerencia'])
def update_producto(request, p_key):
    producto = Productos.objects.get(id=p_key)
    form = AddProductoForm(instance=producto)
    context = {'Producto': producto, 'form': form}
    if request.method == 'POST':
        form = AddProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('ventas')

    return render(request, 'users/update_producto.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria','admin'])
def update_turno(request, t_key):
    
    turno = Turnos.objects.get(id=t_key)
    form = TurnoForm(instance=turno)
    
    context = {'turno': turno, 'form': form}

    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            return redirect('secretaria')

    return render(request, 'users/update_turno.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Ventas','admin'])
def update_venta(request, p_key):
    pedido = Pedidos.objects.get(id=p_key)
    form = PedidoForm(instance=pedido)
    context = {'pedido': pedido, 'form': form}
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('ventas')

    return render(request, 'users/update_venta.html', context)

def unauthorized(request):
    return render(request, 'users/403.html')

