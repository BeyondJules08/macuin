@extends('layouts.app')

@section('content')

<div class="dashboard-container">

<div class="welcome-banner">
⚙️ BIENVENIDOS
</div>


<div class="dashboard-cards">

<div class="dashboard-card">
Pedidos activos
<br>
3 pedidos
</div>

<div class="dashboard-card">
Último pedido
<br>
DR-030
</div>

<div class="dashboard-card">
Crear pedido
<br>
<button class="btn btn-primary">Nuevo</button>
</div>

</div>


<div class="orders-box">

<div class="orders-title">
Pedidos recientes
</div>

<table class="orders-table">

<thead>
<tr>
<th>Folio</th>
<th>Fecha</th>
<th>Estatus</th>
<th>Acción</th>
</tr>
</thead>

<tbody>

<tr>
<td>DR-030</td>
<td>02-oct</td>
<td>Enviado</td>
<td><button class="btn-eye">👁</button></td>
</tr>

<tr>
<td>DR-029</td>
<td>28-sep</td>
<td>Surtido</td>
<td><button class="btn-eye">👁</button></td>
</tr>

</tbody>

</table>

</div>

</div>

@endsection