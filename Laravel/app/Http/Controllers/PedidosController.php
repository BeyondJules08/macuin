<?php

namespace App\Http\Controllers;

use App\Services\FastApiService;
use Illuminate\Http\Request;

class PedidosController extends Controller
{
    private FastApiService $api;

    public function __construct(FastApiService $api)
    {
        $this->api = $api;
    }

    public function index(Request $request)
    {
        $cliente = session('cliente');
        $page    = $request->input('page', 1);
        $estadoId= $request->input('estado', null);

        $params = ['cliente_id' => $cliente['id'], 'page' => $page, 'per_page' => 20];
        if ($estadoId) $params['estado_id'] = $estadoId;

        $pedidosData = $this->api->get('/v1/pedidos/externos/', $params);
        $estadosData = $this->api->getEstadosPedido();

        return view('pedidos', [
            'pedidos'   => $pedidosData['data']  ?? [],
            'total'     => $pedidosData['total'] ?? 0,
            'pages'     => $pedidosData['pages'] ?? 1,
            'page'      => $page,
            'estados'   => $estadosData['data']  ?? [],
            'estado_id' => $estadoId,
        ]);
    }

    public function crear(Request $request)
    {
        $autopartesData = $this->api->getAutopartes(1, '', null);
        $autopartes = $autopartesData ? ($autopartesData['data'] ?? []) : [];
        // Load more pages if needed
        $pages = $autopartesData['pages'] ?? 1;
        for ($p = 2; $p <= min($pages, 10); $p++) {
            $more = $this->api->getAutopartes($p, '', null);
            if ($more) $autopartes = array_merge($autopartes, $more['data'] ?? []);
        }
        return view('pedidos.crear', ['autopartes' => $autopartes]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'autoparte_id'   => 'required|array|min:1',
            'autoparte_id.*' => 'required|integer',
            'cantidad'       => 'required|array|min:1',
            'cantidad.*'     => 'required|integer|min:1',
        ]);

        $items = [];
        foreach ($request->autoparte_id as $idx => $apId) {
            if ($apId && isset($request->cantidad[$idx])) {
                $items[] = ['autoparte_id' => (int)$apId, 'cantidad' => (int)$request->cantidad[$idx]];
            }
        }

        $cliente = session('cliente');
        $result  = $this->api->crearPedidoExterno($cliente['id'], $items, $request->input('notas', ''));

        if ($result && isset($result['status']) && $result['status'] === '201') {
            return redirect('/pedidos')->with('success', 'Pedido creado exitosamente.');
        }

        $error = isset($result['error']) ? $result['error'] :
                (isset($result['detail']) ? $result['detail'] : 'Error al crear el pedido.');
        return back()->withErrors(['general' => $error])->withInput();
    }

    public function detalle(int $id)
    {
        $cliente = session('cliente');
        $data    = $this->api->getPedidoExterno($id);

        if (!$data || !isset($data['data'])) {
            return redirect('/pedidos')->with('error', 'Pedido no encontrado.');
        }

        $pedido = $data['data'];

        // Verify ownership
        if ($pedido['cliente_id'] !== $cliente['id']) {
            return redirect('/pedidos')->with('error', 'No tienes permiso para ver este pedido.');
        }

        $estadosData = $this->api->getEstadosPedido();
        return view('pedidos.detalle', [
            'pedido'  => $pedido,
            'estados' => $estadosData['data'] ?? [],
        ]);
    }
}
