<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Login - MACUIN</title>

<link rel="stylesheet" href="{{ asset('css/dashboard.css') }}">

</head>

<body>

<div class="login-container">

<!-- LADO IZQUIERDO -->

<div class="login-left">

<div class="login-logo">
MACUIN
</div>

<img src="https://cdn-icons-png.flaticon.com/512/2092/2092063.png" class="login-gear">

</div>


<!-- LADO DERECHO -->

<div class="login-box">

<div class="login-avatar">
(Avatar)
</div>

<form method="POST" action="/login">

@csrf

<label>Correo o teléfono</label>
<input type="text" name="email" required>

<label>Contraseña</label>
<input type="password" name="password" required>

<div class="login-forgot">
Olvidé contraseña
</div>

<button type="submit" class="login-btn">
Iniciar sesión
</button>

</form>

</div>

</div>

</body>
</html>