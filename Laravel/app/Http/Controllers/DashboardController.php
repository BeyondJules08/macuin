<?php

namespace App\Http\Controllers;

use App\Services\FastApiService;

class DashboardController extends Controller
{
    private FastApiService $api;

    public function __construct(FastApiService $api)
    {
        $this->api = $api;
    }

    public function index()
    {
        $cliente = session('cliente');
        $stats   = $this->api->getDashboardStats($cliente['id']);

        return view('dashboard', [
            'stats'   => $stats,
            'cliente' => $cliente,
        ]);
    }
}
