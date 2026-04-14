<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'MACUIN - Sistema de Autopartes')</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#2563eb',
                        secondary: '#64748b',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gray-50">

@if(session('cliente'))
<!-- Navegación -->
<nav class="bg-blue-600 text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            <div class="flex items-center">
                <a href="/dashboard" class="flex items-center">
                    <i class="fas fa-car-side text-2xl mr-2"></i>
                    <span class="font-bold text-xl">MACUIN</span>
                </a>
                <div class="hidden md:flex ml-10 space-x-4">
                    <a href="/dashboard" class="px-3 py-2 rounded-md hover:bg-blue-700 transition">
                        <i class="fas fa-home mr-1"></i> Inicio
                    </a>
                    <a href="/catalogo" class="px-3 py-2 rounded-md hover:bg-blue-700 transition">
                        <i class="fas fa-cog mr-1"></i> Catálogo
                    </a>
                    <a href="/pedidos" class="px-3 py-2 rounded-md hover:bg-blue-700 transition">
                        <i class="fas fa-shopping-cart mr-1"></i> Mis Pedidos
                    </a>
                    <a href="/pedidos/crear" class="px-3 py-2 rounded-md hover:bg-blue-700 transition">
                        <i class="fas fa-plus-circle mr-1"></i> Nuevo Pedido
                    </a>
                    <a href="/perfil" class="px-3 py-2 rounded-md hover:bg-blue-700 transition">
                        <i class="fas fa-user mr-1"></i> Mi Cuenta
                    </a>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <div class="text-sm">
                    <span class="font-semibold">{{ session('cliente')['nombre'] ?? '' }}</span>
                    <span class="text-blue-200 ml-2">(Cliente)</span>
                </div>
                <a href="/logout" class="px-4 py-2 bg-blue-700 rounded-md hover:bg-blue-800 transition">
                    <i class="fas fa-sign-out-alt mr-1"></i> Salir
                </a>
            </div>
        </div>
    </div>
    <!-- Menú móvil -->
    <div class="md:hidden px-4 pb-3 space-y-1">
        <a href="/dashboard" class="block px-3 py-2 rounded-md hover:bg-blue-700">Inicio</a>
        <a href="/catalogo"  class="block px-3 py-2 rounded-md hover:bg-blue-700">Catálogo</a>
        <a href="/pedidos"   class="block px-3 py-2 rounded-md hover:bg-blue-700">Mis Pedidos</a>
        <a href="/pedidos/crear" class="block px-3 py-2 rounded-md hover:bg-blue-700">Nuevo Pedido</a>
        <a href="/perfil"    class="block px-3 py-2 rounded-md hover:bg-blue-700">Mi Cuenta</a>
    </div>
</nav>
@endif

<!-- Alertas flash -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
    @if(session('success'))
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
            <i class="fas fa-check-circle mr-2"></i>{{ session('success') }}
        </div>
    @endif
    @if(session('error') || session('warning'))
        <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative mb-4" role="alert">
            <i class="fas fa-exclamation-triangle mr-2"></i>{{ session('error') ?? session('warning') }}
        </div>
    @endif
    @if($errors->any())
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <i class="fas fa-times-circle mr-2"></i>
            @foreach($errors->all() as $error) {{ $error }}@if(!$loop->last), @endif @endforeach
        </div>
    @endif
</div>

<!-- Contenido principal -->
<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    @yield('content')
</main>

<!-- Footer -->
<footer class="bg-gray-800 text-white mt-12">
    <div class="max-w-7xl mx-auto px-4 py-6 text-center">
        <p>&copy; 2024 MACUIN - Sistema de Gestión de Autopartes</p>
        <p class="text-gray-400 text-sm mt-2">Portal para clientes externos</p>
    </div>
</footer>

</body>
</html>
