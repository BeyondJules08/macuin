@extends('layouts.app')
@section('title', 'Nuevo Pedido - MACUIN')

@section('content')
<div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">
        <i class="fas fa-plus-circle mr-2 text-blue-600"></i>Nuevo Pedido
    </h1>
    <p class="text-gray-600 mt-2">Selecciona los productos que deseas solicitar</p>
</div>

@if($errors->has('general'))
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <i class="fas fa-exclamation-circle mr-2"></i>{{ $errors->first('general') }}
    </div>
@endif

<div class="bg-white rounded-lg shadow-md p-6">
    <form method="POST" action="/pedidos/crear" id="pedidoForm">
        @csrf

        <div id="items-container">
            <div class="item-row grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Autoparte</label>
                    <select name="autoparte_id[]" required
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        <option value="">Selecciona una autoparte</option>
                        @foreach($autopartes as $ap)
                            @if($ap['stock_disponible'] > 0)
                            <option value="{{ $ap['id'] }}"
                                    data-precio="{{ $ap['precio'] }}"
                                    data-stock="{{ $ap['stock_disponible'] }}">
                                {{ $ap['nombre'] }}
                                @if($ap['marca']) ({{ $ap['marca'] }})@endif
                                — Stock: {{ $ap['stock_disponible'] }} — ${{ number_format($ap['precio'], 2) }}
                            </option>
                            @endif
                        @endforeach
                    </select>
                </div>
                <div class="flex gap-2 items-end">
                    <div class="flex-1">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Cantidad</label>
                        <input type="number" name="cantidad[]" min="1" required value="1"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <button type="button" onclick="removeItem(this)"
                            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition mb-0">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>

        <button type="button" onclick="addItem()"
                class="mb-6 bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg transition">
            <i class="fas fa-plus mr-2"></i>Agregar Producto
        </button>

        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Notas adicionales (opcional)</label>
            <textarea name="notas" rows="3"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Instrucciones especiales, dirección de entrega, etc.">{{ old('notas') }}</textarea>
        </div>

        <!-- Resumen de precio -->
        <div id="resumen" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 hidden">
            <h3 class="font-semibold text-gray-800 mb-2"><i class="fas fa-receipt mr-2"></i>Resumen del pedido</h3>
            <div id="resumen-items" class="space-y-1 text-sm text-gray-700"></div>
            <div class="border-t border-blue-200 mt-2 pt-2 font-bold text-gray-900">
                Total estimado: $<span id="total-estimado">0.00</span>
            </div>
        </div>

        <div class="flex space-x-3">
            <button type="submit"
                    class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition">
                <i class="fas fa-paper-plane mr-2"></i>Enviar Pedido
            </button>
            <a href="/pedidos" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition">
                Cancelar
            </a>
        </div>
    </form>
</div>

<script>
const autopartesData = @json(collect($autopartes)->keyBy('id'));

function addItem() {
    const container = document.getElementById('items-container');
    const first = container.querySelector('.item-row');
    const clone = first.cloneNode(true);
    clone.querySelector('select').selectedIndex = 0;
    clone.querySelector('input[type=number]').value = 1;
    container.appendChild(clone);
    updateResumen();
}

function removeItem(btn) {
    const container = document.getElementById('items-container');
    if (container.querySelectorAll('.item-row').length > 1) {
        btn.closest('.item-row').remove();
        updateResumen();
    } else {
        alert('Debe haber al menos un producto en el pedido.');
    }
}

function updateResumen() {
    const rows = document.querySelectorAll('.item-row');
    let total = 0;
    const resumenItems = document.getElementById('resumen-items');
    resumenItems.innerHTML = '';
    let hasItem = false;

    rows.forEach(row => {
        const select = row.querySelector('select');
        const qty = parseInt(row.querySelector('input[type=number]').value) || 0;
        const apId = select.value;
        if (apId && qty > 0 && autopartesData[apId]) {
            hasItem = true;
            const ap = autopartesData[apId];
            const subtotal = ap.precio * qty;
            total += subtotal;
            resumenItems.innerHTML += `<div>${ap.nombre} x${qty} = $${subtotal.toFixed(2)}</div>`;
        }
    });

    document.getElementById('total-estimado').textContent = total.toFixed(2);
    document.getElementById('resumen').classList.toggle('hidden', !hasItem);
}

document.getElementById('items-container').addEventListener('change', updateResumen);
document.getElementById('items-container').addEventListener('input', updateResumen);
</script>
@endsection
