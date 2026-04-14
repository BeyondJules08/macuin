@extends('layouts.app')
@section('title', 'Detalle del Pedido - MACUIN')

@section('content')
<div class="mb-6 flex items-center justify-between">
    <div>
        <h1 class="text-3xl font-bold text-gray-900">
            <i class="fas fa-file-alt mr-2 text-blue-600"></i>Pedido EXT-{{ $pedido['id'] }}
        </h1>
        <p class="text-gray-600 mt-1">
            Realizado el
            {{ isset($pedido['fecha_pedido']) ? \Carbon\Carbon::parse($pedido['fecha_pedido'])->format('d/m/Y H:i') : 'N/A' }}
        </p>
    </div>
    <a href="/pedidos" class="bg-gray-500 hover:bg-gray-600 text-white px-5 py-2 rounded-lg transition">
        <i class="fas fa-arrow-left mr-2"></i>Volver
    </a>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

    <!-- Detalles del pedido -->
    <div class="lg:col-span-2 bg-white rounded-lg shadow-md">
        <div class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-bold text-gray-900"><i class="fas fa-list mr-2 text-gray-500"></i>Artículos</h2>
        </div>
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Autoparte</th>
                        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Cantidad</th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Precio Unit.</th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Subtotal</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    @foreach($pedido['detalles'] ?? [] as $detalle)
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 text-sm font-medium text-gray-900">
                            {{ $detalle['autoparte_nombre'] ?? "Autoparte #{$detalle['autoparte_id']}" }}
                        </td>
                        <td class="px-6 py-4 text-center text-sm text-gray-600">{{ $detalle['cantidad'] }}</td>
                        <td class="px-6 py-4 text-right text-sm text-gray-600">${{ number_format($detalle['precio_unitario'], 2) }}</td>
                        <td class="px-6 py-4 text-right text-sm font-bold text-gray-900">${{ number_format($detalle['subtotal'], 2) }}</td>
                    </tr>
                    @endforeach
                </tbody>
                <tfoot class="bg-gray-50">
                    <tr>
                        <td colspan="3" class="px-6 py-4 text-right font-bold text-gray-700">Total</td>
                        <td class="px-6 py-4 text-right font-bold text-lg text-blue-600">${{ number_format($pedido['total'], 2) }}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        @if($pedido['notas'])
        <div class="p-6 border-t border-gray-200">
            <h3 class="text-sm font-medium text-gray-700 mb-2"><i class="fas fa-sticky-note mr-1"></i>Notas</h3>
            <p class="text-sm text-gray-600 bg-yellow-50 border border-yellow-200 rounded p-3">{{ $pedido['notas'] }}</p>
        </div>
        @endif
    </div>

    <!-- Estado del pedido -->
    <div class="space-y-4">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">
                <i class="fas fa-info-circle mr-2 text-blue-500"></i>Estado del Pedido
            </h2>
            @php
                $est = $pedido['estado_nombre'] ?? 'N/A';
                $cls = match($est) {
                    'Pendiente'  => 'bg-yellow-100 text-yellow-800 border-yellow-300',
                    'En Proceso' => 'bg-blue-100 text-blue-800 border-blue-300',
                    'Entregado'  => 'bg-green-100 text-green-800 border-green-300',
                    'Cancelado'  => 'bg-red-100 text-red-800 border-red-300',
                    default      => 'bg-gray-100 text-gray-800 border-gray-300',
                };
                $icon = match($est) {
                    'Pendiente'  => 'fas fa-clock',
                    'En Proceso' => 'fas fa-spinner',
                    'Entregado'  => 'fas fa-check-circle',
                    'Cancelado'  => 'fas fa-times-circle',
                    default      => 'fas fa-question-circle',
                };
            @endphp
            <div class="inline-flex items-center px-4 py-3 rounded-lg border text-lg font-bold {{ $cls }}">
                <i class="{{ $icon }} mr-2"></i>{{ $est }}
            </div>

            <!-- Timeline de estados -->
            <div class="mt-6 space-y-2">
                @foreach(['Pendiente','En Proceso','Entregado'] as $s)
                @php
                    $estados_order = ['Pendiente'=>1,'En Proceso'=>2,'Entregado'=>3,'Cancelado'=>4];
                    $current_order = $estados_order[$est] ?? 0;
                    $step_order    = $estados_order[$s] ?? 0;
                    $done = $current_order >= $step_order && $est !== 'Cancelado';
                @endphp
                <div class="flex items-center">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3 text-xs font-bold
                                {{ $done ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500' }}">
                        {{ $step_order }}
                    </div>
                    <span class="text-sm {{ $done ? 'font-semibold text-gray-800' : 'text-gray-500' }}">{{ $s }}</span>
                </div>
                @endforeach
                @if($est === 'Cancelado')
                <div class="flex items-center">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3 bg-red-600 text-white text-xs font-bold">
                        <i class="fas fa-times"></i>
                    </div>
                    <span class="text-sm font-semibold text-red-700">Cancelado</span>
                </div>
                @endif
            </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-3">
                <i class="fas fa-receipt mr-2 text-gray-500"></i>Resumen
            </h2>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="text-gray-600">Artículos:</span>
                    <span class="font-medium">{{ count($pedido['detalles'] ?? []) }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Folio:</span>
                    <span class="font-medium">EXT-{{ $pedido['id'] }}</span>
                </div>
                <div class="flex justify-between border-t pt-2 mt-2">
                    <span class="font-bold text-gray-800">Total:</span>
                    <span class="font-bold text-blue-600 text-lg">${{ number_format($pedido['total'], 2) }}</span>
                </div>
            </div>
        </div>

        <a href="/pedidos" class="block w-full text-center bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-3 rounded-lg transition font-medium">
            <i class="fas fa-arrow-left mr-2"></i>Volver a Mis Pedidos
        </a>
    </div>
</div>
@endsection
