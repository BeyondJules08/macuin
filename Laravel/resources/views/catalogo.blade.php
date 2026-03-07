@extends('layouts.app')

@section('content')

<h1>Catálogo</h1>


<div class="catalog-categories">

<div class="category-card">
<img src="/img/piezas.png" width="80">
Piezas
</div>

<div class="category-card">
<img src="/img/accesorios.png" width="80">
Accesorios
</div>

<div class="category-card">
<img src="/img/ofertas.png" width="80">
Ofertas
</div>

</div>


<div class="catalog-filter">

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
<option>Disponible</option>
<option>Sin stock</option>
</select>

<button class="btn-filter">
Aplicar Filtro
</button>

</div>


<div class="catalog-table">

<table>

<thead>

<tr>
<th>Código</th>
<th>Autoparte</th>
<th>Categoría</th>
<th>Disponibilidad</th>
</tr>

</thead>

<tbody>

<tr>
<td>FR-001</td>
<td>Balatas delanteras</td>
<td>Frenos</td>
<td>Disponible</td>
</tr>

<tr>
<td>MT-014</td>
<td>Filtro de aceite</td>
<td>Motor</td>
<td>Disponible</td>
</tr>

<tr>
<td>SU-022</td>
<td>Amortiguador trasero</td>
<td>Suspensión</td>
<td>Sin stock</td>
</tr>

<tr>
<td>EL-009</td>
<td>Batería 12V</td>
<td>Eléctrico</td>
<td>Disponible</td>
</tr>

<tr>
<td>DR-030</td>
<td>Disco de freno</td>
<td>Frenos</td>
<td>Disponible</td>
</tr>

</tbody>

</table>

</div>

@endsection