@extends('layouts.app')
@section('title', 'Catálogo - MACUIN')

@section('content')
<div class="mb-8 flex items-center justify-between">
    <div>
        <h1 class="text-3xl font-bold text-gray-900">
            <i class="fas fa-cog mr-2 text-blue-600"></i>Catálogo de Autopartes
        </h1>
        <p class="text-gray-600 mt-2">Explora nuestro inventario de autopartes disponibles</p>
    </div>
    <a href="/pedidos/crear"
       class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md">
        <i class="fas fa-shopping-cart mr-2"></i>Hacer Pedido
    </a>
</div>

<!-- Filtros -->
<div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <form method="GET" action="/catalogo" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
            <input type="text" name="search" value="{{ $search }}"
                   placeholder="Nombre o marca..."
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Categoría</label>
            <select name="categoria" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="">Todas las categorías</option>
                @foreach($categorias as $cat)
                    <option value="{{ $cat['id'] }}" {{ $categoria_id == $cat['id'] ? 'selected' : '' }}>
                        {{ $cat['nombre'] }}
                    </option>
                @endforeach
            </select>
        </div>
        <div class="flex items-end space-x-2">
            <button type="submit" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition">
                <i class="fas fa-search mr-2"></i>Buscar
            </button>
            <a href="/catalogo" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition">
                <i class="fas fa-redo"></i>
            </a>
        </div>
    </form>
</div>

<!-- Tabla -->
<div class="bg-white rounded-lg shadow-md overflow-hidden">
    <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Autoparte</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoría</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marca</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precio</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Disponibilidad</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                @forelse($autopartes as $ap)
                <tr class="hover:bg-gray-50 transition">
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">#{{ $ap['id'] }}</td>
                    <td class="px-6 py-4">
                        <div class="text-sm font-medium text-gray-900">{{ $ap['nombre'] }}</div>
                        <div class="text-sm text-gray-500">{{ Str::limit($ap['descripcion'] ?? '', 50) }}</div>
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-block px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                            {{ $ap['categoria']['nombre'] ?? 'N/A' }}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">{{ $ap['marca'] ?? 'N/A' }}</td>
                    <td class="px-6 py-4 text-sm font-semibold text-gray-900">${{ number_format($ap['precio'], 2) }}</td>
                    <td class="px-6 py-4">
                        @if($ap['stock_disponible'] > 0)
                            <span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                <i class="fas fa-check mr-1"></i>Disponible ({{ $ap['stock_disponible'] }})
                            </span>
                        @else
                            <span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                <i class="fas fa-times mr-1"></i>Sin stock
                            </span>
                        @endif
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-2"></i>
                        <p>No se encontraron autopartes</p>
                    </td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>
</div>

<!-- Paginación -->
@if($pages > 1)
<div class="mt-6 flex justify-center">
    <nav class="inline-flex rounded-md shadow-sm -space-x-px">
        @if($page > 1)
            <a href="/catalogo?page={{ $page - 1 }}&search={{ $search }}&categoria={{ $categoria_id }}"
               class="px-4 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                <i class="fas fa-chevron-left"></i>
            </a>
        @endif
        @for($p = 1; $p <= $pages; $p++)
            @if($p == $page)
                <span class="px-4 py-2 border border-blue-500 bg-blue-50 text-sm font-medium text-blue-600">{{ $p }}</span>
            @else
                <a href="/catalogo?page={{ $p }}&search={{ $search }}&categoria={{ $categoria_id }}"
                   class="px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">{{ $p }}</a>
            @endif
        @endfor
        @if($page < $pages)
            <a href="/catalogo?page={{ $page + 1 }}&search={{ $search }}&categoria={{ $categoria_id }}"
               class="px-4 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                <i class="fas fa-chevron-right"></i>
            </a>
        @endif
    </nav>
</div>
@endif
@endsection
