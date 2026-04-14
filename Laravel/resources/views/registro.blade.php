<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro - MACUIN</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-blue-700 py-8">
    <div class="max-w-md w-full space-y-6 bg-white p-10 rounded-xl shadow-2xl mx-4">
        <div class="text-center">
            <div class="flex justify-center">
                <i class="fas fa-user-plus text-5xl text-blue-600"></i>
            </div>
            <h2 class="mt-4 text-3xl font-extrabold text-gray-900">Crear Cuenta</h2>
            <p class="mt-2 text-sm text-gray-600">Regístrate para acceder al catálogo y hacer pedidos</p>
        </div>

        @if($errors->any())
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                <i class="fas fa-times-circle mr-1"></i>
                @foreach($errors->all() as $error){{ $error }}@endforeach
            </div>
        @endif

        <form class="space-y-4" method="POST" action="/registro">
            @csrf
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-user text-gray-400"></i>
                    </div>
                    <input name="nombre" type="text" required value="{{ old('nombre') }}"
                           class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                           placeholder="Tu nombre completo">
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico *</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-envelope text-gray-400"></i>
                    </div>
                    <input name="email" type="email" required value="{{ old('email') }}"
                           class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                           placeholder="correo@ejemplo.com">
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-lock text-gray-400"></i>
                    </div>
                    <input name="password" type="password" required
                           class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                           placeholder="Mínimo 6 caracteres">
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar Contraseña *</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-lock text-gray-400"></i>
                    </div>
                    <input name="password_confirmation" type="password" required
                           class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                           placeholder="Repite tu contraseña">
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono (opcional)</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-phone text-gray-400"></i>
                    </div>
                    <input name="telefono" type="text" value="{{ old('telefono') }}"
                           class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                           placeholder="Tu número de teléfono">
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Dirección (opcional)</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-map-marker-alt text-gray-400"></i>
                    </div>
                    <input name="direccion" type="text" value="{{ old('direccion') }}"
                           class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                           placeholder="Tu dirección de entrega">
                </div>
            </div>
            <button type="submit"
                    class="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none transition">
                <i class="fas fa-user-plus mr-2"></i>Crear Cuenta
            </button>
        </form>

        <div class="text-center">
            <p class="text-sm text-gray-600">
                ¿Ya tienes cuenta?
                <a href="/login" class="font-medium text-blue-600 hover:text-blue-500">Inicia sesión</a>
            </p>
        </div>
    </div>
</div>
</body>
</html>
