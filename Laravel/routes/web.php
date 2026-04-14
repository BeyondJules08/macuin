<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\CatalogoController;
use App\Http\Controllers\PedidosController;
use App\Http\Controllers\PerfilController;

// ── Rutas públicas ────────────────────────────────────────────────────

Route::get('/login',    [AuthController::class, 'showLogin'])->name('login');
Route::post('/login',   [AuthController::class, 'login']);
Route::get('/registro', [AuthController::class, 'showRegistro'])->name('registro');
Route::post('/registro',[AuthController::class, 'registro']);
Route::get('/logout',   [AuthController::class, 'logout'])->name('logout');

// ── Rutas protegidas (requieren sesión activa) ─────────────────────────

Route::middleware(\App\Http\Middleware\CheckSession::class)->group(function () {

    Route::get('/',          [DashboardController::class, 'index']);
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');

    Route::get('/catalogo',  [CatalogoController::class, 'index'])->name('catalogo');

    Route::get('/pedidos',         [PedidosController::class, 'index'])->name('pedidos');
    Route::get('/pedidos/crear',   [PedidosController::class, 'crear'])->name('pedidos.crear');
    Route::post('/pedidos/crear',  [PedidosController::class, 'store'])->name('pedidos.store');
    Route::get('/pedidos/{id}',    [PedidosController::class, 'detalle'])->name('pedidos.detalle');

    Route::get('/perfil',         [PerfilController::class, 'index'])->name('perfil');
    Route::post('/perfil/update', [PerfilController::class, 'update'])->name('perfil.update');
});
