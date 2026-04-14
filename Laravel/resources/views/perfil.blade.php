@extends('layouts.app')
@section('title', 'Mi Perfil - MACUIN')

@section('content')
<div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">
        <i class="fas fa-user-circle mr-2 text-blue-600"></i>Mi Perfil
    </h1>
    <p class="text-gray-600 mt-2">Administra tu información personal</p>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

    <!-- Tarjeta perfil -->
    <div class="bg-white rounded-lg shadow-md p-6 text-center">
        <div class="w-32 h-32 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
            <i class="fas fa-user text-5xl text-blue-600"></i>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">{{ $cliente['nombre'] }}</h2>
        <p class="text-gray-500 mt-1">{{ $cliente['email'] }}</p>
        <span class="inline-block mt-3 px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
            <i class="fas fa-check-circle mr-1"></i>
            {{ ($cliente['activo'] ?? true) ? 'Activo' : 'Inactivo' }}
        </span>
        <div class="mt-4 pt-4 border-t border-gray-100 text-left space-y-2">
            @if($cliente['telefono'])
            <div class="flex items-center text-sm text-gray-600">
                <i class="fas fa-phone mr-2 text-gray-400 w-4"></i>
                {{ $cliente['telefono'] }}
            </div>
            @endif
            @if($cliente['direccion'])
            <div class="flex items-center text-sm text-gray-600">
                <i class="fas fa-map-marker-alt mr-2 text-gray-400 w-4"></i>
                {{ $cliente['direccion'] }}
            </div>
            @endif
            @if($cliente['fecha_registro'])
            <div class="flex items-center text-sm text-gray-600">
                <i class="fas fa-calendar mr-2 text-gray-400 w-4"></i>
                Miembro desde {{ \Carbon\Carbon::parse($cliente['fecha_registro'])->format('d/m/Y') }}
            </div>
            @endif
        </div>
    </div>

    <!-- Formulario edición -->
    <div class="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6">
            <i class="fas fa-edit mr-2 text-blue-500"></i>Editar Información
        </h2>

        <form method="POST" action="/perfil/update" class="space-y-5">
            @csrf
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Nombre completo *</label>
                    <input name="nombre" type="text" required value="{{ old('nombre', $cliente['nombre']) }}"
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Correo electrónico</label>
                    <input type="email" value="{{ $cliente['email'] }}" disabled
                           class="w-full px-4 py-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed">
                    <p class="text-xs text-gray-400 mt-1">El correo no se puede cambiar.</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Teléfono</label>
                    <input name="telefono" type="text" value="{{ old('telefono', $cliente['telefono'] ?? '') }}"
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="Tu número de teléfono">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Dirección</label>
                    <input name="direccion" type="text" value="{{ old('direccion', $cliente['direccion'] ?? '') }}"
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="Tu dirección de entrega">
                </div>
            </div>

            <hr class="my-2">
            <h3 class="text-lg font-semibold text-gray-800">
                <i class="fas fa-lock mr-2 text-gray-500"></i>Cambiar Contraseña
                <span class="text-sm font-normal text-gray-500">(dejar en blanco para no cambiar)</span>
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Nueva contraseña</label>
                    <input name="password" type="password"
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="Mínimo 6 caracteres">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Confirmar contraseña</label>
                    <input name="password_confirmation" type="password"
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           placeholder="Repite la contraseña">
                </div>
            </div>

            <div class="flex space-x-3 pt-2">
                <button type="submit"
                        class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition">
                    <i class="fas fa-save mr-2"></i>Guardar Cambios
                </button>
                <a href="/dashboard" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition">
                    Cancelar
                </a>
            </div>
        </form>
    </div>
</div>
@endsection
