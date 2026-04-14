<?php

namespace App\Http\Controllers;

use App\Services\FastApiService;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    private FastApiService $api;

    public function __construct(FastApiService $api)
    {
        $this->api = $api;
    }

    public function showLogin()
    {
        if (session('cliente')) {
            return redirect('/dashboard');
        }
        return view('login');
    }

    public function login(Request $request)
    {
        $request->validate([
            'email'    => 'required|email',
            'password' => 'required',
        ]);

        $result = $this->api->authenticateClient($request->email, $request->password);

        if ($result && isset($result['status']) && $result['status'] === '200') {
            $clienteData = $result['data'];
            session(['cliente' => $clienteData]);
            // Store credentials for JWT auto-refresh
            session(['_api_email' => $request->email]);
            session(['_api_password' => $request->password]);
            return redirect('/dashboard')->with('success', '¡Bienvenido ' . $clienteData['nombre'] . '!');
        }

        $msg = isset($result['detail']) ? $result['detail'] : 'Email o contraseña incorrectos.';
        return back()->withErrors(['email' => $msg])->withInput($request->only('email'));
    }

    public function showRegistro()
    {
        if (session('cliente')) {
            return redirect('/dashboard');
        }
        return view('registro');
    }

    public function registro(Request $request)
    {
        $request->validate([
            'nombre'   => 'required|min:3|max:100',
            'email'    => 'required|email',
            'password' => 'required|min:6|confirmed',
            'telefono' => 'nullable|max:20',
            'direccion'=> 'nullable|max:200',
        ]);

        $result = $this->api->registrarCliente([
            'nombre'   => $request->nombre,
            'email'    => $request->email,
            'password' => $request->password,
            'telefono' => $request->telefono,
            'direccion'=> $request->direccion,
        ]);

        if ($result && isset($result['status']) && $result['status'] === '201') {
            return redirect('/login')->with('success', 'Cuenta creada exitosamente. Ya puedes iniciar sesión.');
        }

        $error = isset($result['error']) ? $result['error'] :
                (isset($result['detail']) ? $result['detail'] : 'Error al registrar. Intenta de nuevo.');
        return back()->withErrors(['email' => $error])->withInput($request->except('password', 'password_confirmation'));
    }

    public function logout()
    {
        session()->forget(['cliente', '_api_email', '_api_password']);
        return redirect('/login')->with('success', 'Has cerrado sesión.');
    }
}
