<?php

namespace App\Http\Controllers;

use App\Services\FastApiService;
use Illuminate\Http\Request;

class CatalogoController extends Controller
{
    private FastApiService $api;

    public function __construct(FastApiService $api)
    {
        $this->api = $api;
    }

    public function index(Request $request)
    {
        $page       = $request->input('page', 1);
        $search     = $request->input('search', '');
        $categoriaId= $request->input('categoria', null);

        $autopartesData = $this->api->getAutopartes($page, $search, $categoriaId);
        $categoriasData = $this->api->getCategorias();

        return view('catalogo', [
            'autopartes' => $autopartesData['data']   ?? [],
            'total'      => $autopartesData['total']  ?? 0,
            'pages'      => $autopartesData['pages']  ?? 1,
            'page'       => $page,
            'categorias' => $categoriasData['data']   ?? [],
            'search'     => $search,
            'categoria_id'=> (int) $categoriaId,
        ]);
    }
}
