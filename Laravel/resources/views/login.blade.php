<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - MACUIN</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-blue-700">
    <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-2xl mx-4">
        <div class="text-center">
            <div class="flex justify-center">
                <i class="fas fa-car-side text-6xl text-blue-600"></i>
            </div>
            <h2 class="mt-6 text-3xl font-extrabold text-gray-900">MACUIN</h2>
            <p class="mt-2 text-sm text-gray-600">Portal de Clientes - Autopartes</p>
        </div>

        @if(session('success'))
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded text-sm">
                <i class="fas fa-check-circle mr-1"></i>{{ session('success') }}
            </div>
        @endif

        @if($errors->any())
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                <i class="fas fa-times-circle mr-1"></i>
                @foreach($errors->all() as $error){{ $error }}@endforeach
            </div>
        @endif

        <form class="mt-8 space-y-6" method="POST" action="/login">
            @csrf
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <i class="fas fa-envelope text-gray-400"></i>
                        </div>
                        <input name="email" type="email" required value="{{ old('email') }}"
                               class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                               placeholder="correo@ejemplo.com">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <i class="fas fa-lock text-gray-400"></i>
                        </div>
                        <input name="password" type="password" required
                               class="appearance-none rounded-lg block w-full pl-10 pr-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm"
                               placeholder="••••••••">
                    </div>
                </div>
            </div>
            <button type="submit"
                    class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition">
                <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                    <i class="fas fa-sign-in-alt text-blue-300 group-hover:text-blue-200"></i>
                </span>
                Iniciar Sesión
            </button>
        </form>

        <div class="text-center">
            <p class="text-sm text-gray-600">
                ¿No tienes cuenta?
                <a href="/registro" class="font-medium text-blue-600 hover:text-blue-500">Regístrate aquí</a>
            </p>
        </div>
    </div>
</div>
</body>
</html>
