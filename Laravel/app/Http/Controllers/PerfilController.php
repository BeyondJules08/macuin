<?php

namespace App\Http\Controllers;

use App\Services\FastApiService;
use Illuminate\Http\Request;

class PerfilController extends Controller
{
    private FastApiService $api;

    public function __construct(FastApiService $api)
    {
        $this->api = $api;
    }

    public function index()
    {
        $cliente = session('cliente');
        // Refresh data from API
        $data = $this->api->get("/v1/clientes/{$cliente['id']}");
        if ($data && isset($data['data'])) {
            $cliente = $data['data'];
            session(['cliente' => $cliente]);
        }
        return view('perfil', ['cliente' => $cliente]);
    }

    public function update(Request $request)
    {
        $request->validate([
            'nombre'   => 'required|min:3|max:100',
            'telefono' => 'nullable|max:20',
            'direccion'=> 'nullable|max:200',
        ]);

        $cliente = session('cliente');
        $payload = [
            'nombre'   => $request->nombre,
            'telefono' => $request->telefono,
            'direccion'=> $request->direccion,
        ];

        if ($request->filled('password')) {
            $request->validate(['password' => 'min:6|confirmed']);
            $payload['password'] = $request->password;
        }

        $result = $this->api->put("/v1/clientes/{$cliente['id']}", $payload);

        if ($result && isset($result['data'])) {
            session(['cliente' => $result['data']]);
            return back()->with('success', 'Perfil actualizado correctamente.');
        }
        return back()->withErrors(['general' => 'Error al actualizar perfil.']);
    }
}
