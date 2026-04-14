@extends('layouts.app')
@section('title', 'Mis Pedidos - MACUIN')

@section('content')
<div class="mb-8 flex justify-between items-center">
    <div>
        <h1 class="text-3xl font-bold text-gray-900">
            <i class="fas fa-shopping-cart mr-2 text-purple-600"></i>Mis Pedidos
        </h1>
        <p class="text-gray-600 mt-2">Historial de tus pedidos realizados</p>
    </div>
    <a href="/pedidos/crear"
       class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md">
        <i class="fas fa-plus mr-2"></i>Nuevo Pedido
    </a>
</div>

<!-- Filtros -->
<div class="bg-white rounded-lg shadow-md p-4 mb-6">
    <form method="GET" action="/pedidos" class="flex flex-wrap gap-4 items-end">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Filtrar por estado</label>
            <select name="estado" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="">Todos los estados</option>
                @foreach($estados as $est)
                    <option value="{{ $est['id'] }}" {{ $estado_id == $est['id'] ? 'selected' : '' }}>
                        {{ $est['nombre'] }}
                    </option>
                @endforeach
            </select>
        </div>
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition">
            <i class="fas fa-filter mr-1"></i>Filtrar
        </button>
        <a href="/pedidos" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition">
            <i class="fas fa-redo"></i>
        </a>
    </form>
</div>

<!-- Tabla -->
<div class="bg-white rounded-lg shadow-md overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Folio</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Artículos</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Acción</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
            @forelse($pedidos as $pedido)
            <tr class="hover:bg-gray-50 transition">
                <td class="px-6 py-4 text-sm font-medium text-gray-900">EXT-{{ $pedido['id'] }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">
                    {{ isset($pedido['fecha_pedido']) ? \Carbon\Carbon::parse($pedido['fecha_pedido'])->format('d/m/Y') : 'N/A' }}
                </td>
                <td class="px-6 py-4">
                    @php
                        $est = $pedido['estado_nombre'] ?? 'N/A';
                        $cls = match($est) {
                            'Pendiente'  => 'bg-yellow-100 text-yellow-800',
                            'En Proceso' => 'bg-blue-100 text-blue-800',
                            'Entregado'  => 'bg-green-100 text-green-800',
                            'Cancelado'  => 'bg-red-100 text-red-800',
                            default      => 'bg-gray-100 text-gray-800',
                        };
                    @endphp
                    <span class="px-2 py-1 text-xs font-semibold rounded-full {{ $cls }}">{{ $est }}</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600">{{ count($pedido['detalles'] ?? []) }} artículo(s)</td>
                <td class="px-6 py-4 font-bold text-gray-900">${{ number_format($pedido['total'], 2) }}</td>
                <td class="px-6 py-4 text-center">
                    <a href="/pedidos/{{ $pedido['id'] }}" class="text-blue-600 hover:text-blue-900 mx-1" title="Ver detalle">
                        <i class="fas fa-eye"></i>
                    </a>
                </td>
            </tr>
            @empty
            <tr>
                <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2 block"></i>
                    No tienes pedidos registrados.
                    <a href="/pedidos/crear" class="text-blue-600 hover:underline ml-1">Crear tu primer pedido</a>
                </td>
            </tr>
            @endforelse
        </tbody>
    </table>
</div>

<!-- Paginación -->
@if($pages > 1)
<div class="mt-6 flex justify-center">
    <nav class="inline-flex rounded-md shadow-sm -space-x-px">
        @if($page > 1)
            <a href="/pedidos?page={{ $page - 1 }}&estado={{ $estado_id }}"
               class="px-4 py-2 rounded-l-md border border-gray-300 bg-white text-sm text-gray-500 hover:bg-gray-50">
                <i class="fas fa-chevron-left"></i>
            </a>
        @endif
        @for($p = 1; $p <= $pages; $p++)
            @if($p == $page)
                <span class="px-4 py-2 border border-blue-500 bg-blue-50 text-sm font-medium text-blue-600">{{ $p }}</span>
            @else
                <a href="/pedidos?page={{ $p }}&estado={{ $estado_id }}"
                   class="px-4 py-2 border border-gray-300 bg-white text-sm text-gray-700 hover:bg-gray-50">{{ $p }}</a>
            @endif
        @endfor
        @if($page < $pages)
            <a href="/pedidos?page={{ $page + 1 }}&estado={{ $estado_id }}"
               class="px-4 py-2 rounded-r-md border border-gray-300 bg-white text-sm text-gray-500 hover:bg-gray-50">
                <i class="fas fa-chevron-right"></i>
            </a>
        @endif
    </nav>
</div>
@endif
@endsection
