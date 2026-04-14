@extends('layouts.app')
@section('title', 'Dashboard - MACUIN')

@section('content')
<div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">
        <i class="fas fa-home mr-2 text-blue-600"></i>Dashboard
    </h1>
    <p class="text-gray-600 mt-2">Bienvenido, <strong>{{ $cliente['nombre'] }}</strong></p>
</div>

<!-- Estadísticas -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-600 font-semibold">Total Pedidos</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ $stats['total_pedidos'] }}</p>
            </div>
            <div class="bg-blue-100 rounded-full p-4">
                <i class="fas fa-shopping-cart text-2xl text-blue-600"></i>
            </div>
        </div>
    </div>

    <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-600 font-semibold">Pedidos Activos</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ $stats['pedidos_activos'] }}</p>
            </div>
            <div class="bg-yellow-100 rounded-full p-4">
                <i class="fas fa-clock text-2xl text-yellow-600"></i>
            </div>
        </div>
    </div>

    <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-600 font-semibold">Acceso Rápido</p>
                <a href="/pedidos/crear" class="inline-block mt-3 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition">
                    <i class="fas fa-plus mr-1"></i>Nuevo Pedido
                </a>
            </div>
            <div class="bg-purple-100 rounded-full p-4">
                <i class="fas fa-bolt text-2xl text-purple-600"></i>
            </div>
        </div>
    </div>
</div>

<!-- Pedidos recientes -->
<div class="bg-white rounded-lg shadow-md">
    <div class="p-6 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900 flex items-center">
            <i class="fas fa-history text-blue-500 mr-2"></i>Pedidos Recientes
        </h2>
        <a href="/pedidos" class="text-blue-600 hover:text-blue-800 text-sm font-medium">Ver todos</a>
    </div>
    <div class="p-6">
        @if(count($stats['pedidos_recientes']) > 0)
            <div class="space-y-4">
                @foreach($stats['pedidos_recientes'] as $pedido)
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition">
                    <div class="flex-1">
                        <p class="font-semibold text-gray-900">Pedido #EXT-{{ $pedido['id'] }}</p>
                        <p class="text-xs text-gray-500">
                            {{ isset($pedido['fecha_pedido']) ? \Carbon\Carbon::parse($pedido['fecha_pedido'])->format('d/m/Y H:i') : 'N/A' }}
                        </p>
                    </div>
                    <div class="text-right mr-4">
                        @php
                            $estado = $pedido['estado_nombre'] ?? 'N/A';
                            $colorClass = match($estado) {
                                'Pendiente'  => 'bg-yellow-100 text-yellow-800',
                                'En Proceso' => 'bg-blue-100 text-blue-800',
                                'Entregado'  => 'bg-green-100 text-green-800',
                                'Cancelado'  => 'bg-red-100 text-red-800',
                                default      => 'bg-gray-100 text-gray-800',
                            };
                        @endphp
                        <span class="inline-block px-3 py-1 text-xs font-semibold rounded-full {{ $colorClass }}">
                            {{ $estado }}
                        </span>
                        <p class="text-lg font-bold text-gray-900 mt-1">${{ number_format($pedido['total'], 2) }}</p>
                    </div>
                    <a href="/pedidos/{{ $pedido['id'] }}" class="text-blue-600 hover:text-blue-900">
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
                @endforeach
            </div>
        @else
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-inbox text-4xl mb-2"></i>
                <p>No tienes pedidos registrados aún.</p>
                <a href="/pedidos/crear" class="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition">
                    <i class="fas fa-plus mr-1"></i>Crear tu primer pedido
                </a>
            </div>
        @endif
    </div>
</div>

<!-- Enlaces rápidos -->
<div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
    <a href="/catalogo"
       class="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border-t-4 border-blue-500">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-lg font-semibold text-gray-900">Ver Catálogo</h3>
                <p class="text-sm text-gray-600 mt-1">Explora nuestras autopartes</p>
            </div>
            <i class="fas fa-cog text-3xl text-blue-500"></i>
        </div>
    </a>
    <a href="/pedidos/crear"
       class="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border-t-4 border-purple-500">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-lg font-semibold text-gray-900">Nuevo Pedido</h3>
                <p class="text-sm text-gray-600 mt-1">Solicita autopartes</p>
            </div>
            <i class="fas fa-plus-circle text-3xl text-purple-500"></i>
        </div>
    </a>
    <a href="/perfil"
       class="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border-t-4 border-green-500">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-lg font-semibold text-gray-900">Mi Perfil</h3>
                <p class="text-sm text-gray-600 mt-1">Administra tu cuenta</p>
            </div>
            <i class="fas fa-user text-3xl text-green-500"></i>
        </div>
    </a>
</div>
@endsection
