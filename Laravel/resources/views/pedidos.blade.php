@extends('layouts.app')

@section('content')

<h1>Mis pedidos</h1>


<div class="orders-stats">

<div class="stat-card">
<img src="/img/pedidos.png" width="60">
Total de pedidos
</div>

<div class="stat-card">
<img src="/img/activos.png" width="60">
Pedidos activos
</div>

<div class="stat-card">
<img src="/img/enviados.png" width="60">
Pedidos enviados
</div>

</div>


<div class="orders-filter">

<input type="text" placeholder="Buscar producto...">

<select>
<option>Categoría</option>
<option>Frenos</option>
<option>Motor</option>
<option>Suspensión</option>
<option>Eléctrico</option>
</select>

<select>
<option>Todo</option>
<option>Enviado</option>
<option>Surtido</option>
<option>Cancelado</option>
</select>

<button>
Aplicar Filtro
</button>

</div>


<div class="orders-table-container">

<table class="orders-table">

<thead>
<tr>
<th>Folio</th>
<th>Fecha</th>
<th>Estatus</th>
<th>Artículos</th>
<th>Acción</th>
</tr>
</thead>

<tbody>

<tr>
<td>DR-030</td>
<td>02/10/2025</td>
<td>Enviado</td>
<td>5</td>
<td>
<button class="action-btn">👁</button>
<button class="action-btn">🗑</button>
</td>
</tr>

<tr>
<td>DR-029</td>
<td>28/09/2025</td>
<td>Surtido</td>
<td>3</td>
<td>
<button class="action-btn">👁</button>
<button class="action-btn">🗑</button>
</td>
</tr>

<tr>
<td>DR-028</td>
<td>25/09/2025</td>
<td>Recibido</td>
<td>4</td>
<td>
<button class="action-btn">👁</button>
<button class="action-btn">🗑</button>
</td>
</tr>

<tr>
<td>DR-027</td>
<td>20/09/2025</td>
<td>Cancelado</td>
<td>2</td>
<td>
<button class="action-btn">👁</button>
<button class="action-btn">🗑</button>
</td>
</tr>

<tr>
<td>DR-026</td>
<td>18/09/2025</td>
<td>Enviado</td>
<td>6</td>
<td>
<button class="action-btn">👁</button>
<button class="action-btn">🗑</button>
</td>
</tr>

</tbody>

</table>

</div>

@endsection