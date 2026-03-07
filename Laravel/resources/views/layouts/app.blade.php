<!DOCTYPE html>
<html lang="es">

<head>

<meta charset="UTF-8">
<title>MACUIN Sistema</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

<link rel="stylesheet" href="{{ asset('css/dashboard.css') }}">

</head>


<body>

<!-- HEADER -->

<div class="topbar">
Sistema de Gestión de Autopartes
</div>


<!-- SIDEBAR -->

<div class="sidebar">

<h2>MACUIN</h2>

<a href="/dashboard">INICIO</a>
<a href="/pedidos">MIS PEDIDOS</a>
<a href="/catalogo">CATALOGO</a>
<a href="/perfil">MI CUENTA</a>

</div>


<!-- CONTENIDO -->

<div class="content">

@yield('content')

</div>


</body>
</html>