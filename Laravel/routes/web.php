<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('dashboard');
});

Route::get('/dashboard', function () {
    return view('dashboard');
});

Route::get('/catalogo', function () {
    return view('catalogo');
});

Route::get('/pedidos', function () {
    return view('pedidos');
});

Route::get('/perfil', function () {
    return view('perfil');
});

use Illuminate\Http\Request;

Route::get('/login', function () {
    return view('login');
});

Route::post('/login', function (Request $request) {
    return redirect('/dashboard');
});

Route::get('/dashboard', function () {
    return view('dashboard');
});