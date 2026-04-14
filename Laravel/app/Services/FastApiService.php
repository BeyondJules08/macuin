<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Client\RequestException;

class FastApiService
{
    private string $baseUrl;
    private string $apiKey;

    public function __construct()
    {
        $this->baseUrl = env('API_URL', 'http://fastapi:8080');
        $this->apiKey  = env('API_KEY', 'macuin_api_key_2024');
    }

    private function headers(): array
    {
        return ['X-API-Key' => $this->apiKey];
    }

    public function get(string $path, array $params = []): ?array
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(10)
                ->get($this->baseUrl . $path, $params);
            return $response->successful() ? $response->json() : null;
        } catch (\Exception $e) {
            return null;
        }
    }

    public function post(string $path, array $data): ?array
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(10)
                ->post($this->baseUrl . $path, $data);
            if ($response->status() === 422) {
                return ['error' => $response->json('detail', 'Error de validación')];
            }
            return $response->json();
        } catch (\Exception $e) {
            return ['error' => $e->getMessage()];
        }
    }

    public function put(string $path, array $data): ?array
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(10)
                ->put($this->baseUrl . $path, $data);
            return $response->json();
        } catch (\Exception $e) {
            return null;
        }
    }

    public function delete(string $path): ?array
    {
        try {
            $response = Http::withHeaders($this->headers())
                ->timeout(10)
                ->delete($this->baseUrl . $path);
            return $response->json();
        } catch (\Exception $e) {
            return null;
        }
    }

    // ── Auth ─────────────────────────────────────────────────────────

    public function loginCliente(string $email, string $password): ?array
    {
        return $this->post('/v1/auth/login-cliente', compact('email', 'password'));
    }

    public function registrarCliente(array $data): ?array
    {
        return $this->post('/v1/clientes/registro', $data);
    }

    // ── Catálogo ──────────────────────────────────────────────────────

    public function getAutopartes(int $page = 1, string $search = '', ?int $categoriaId = null): ?array
    {
        $params = ['page' => $page, 'per_page' => 20, 'solo_activos' => 'true'];
        if ($search) $params['search'] = $search;
        if ($categoriaId) $params['categoria_id'] = $categoriaId;
        return $this->get('/v1/autopartes/', $params);
    }

    public function getCategorias(): ?array
    {
        return $this->get('/v1/categorias/');
    }

    // ── Pedidos externos ──────────────────────────────────────────────

    public function getPedidosCliente(int $clienteId, int $page = 1): ?array
    {
        return $this->get('/v1/pedidos/externos/', ['cliente_id' => $clienteId, 'page' => $page, 'per_page' => 20]);
    }

    public function getPedidoExterno(int $id): ?array
    {
        return $this->get("/v1/pedidos/externos/{$id}");
    }

    public function crearPedidoExterno(int $clienteId, array $items, string $notas = ''): ?array
    {
        $payload = ['cliente_id' => $clienteId, 'items' => $items];
        if ($notas) $payload['notas'] = $notas;
        return $this->post('/v1/pedidos/externos/', $payload);
    }

    public function getEstadosPedido(): ?array
    {
        return $this->get('/v1/pedidos/estados/');
    }

    // ── Dashboard stats ────────────────────────────────────────────────

    public function getDashboardStats(int $clienteId): array
    {
        $pedidos = $this->getPedidosCliente($clienteId, 1);
        $recientes = $pedidos['data'] ?? [];
        $total = $pedidos['total'] ?? 0;
        $activos = collect($recientes)->whereIn('estado_nombre', ['Pendiente', 'En Proceso'])->count();
        return [
            'total_pedidos' => $total,
            'pedidos_activos' => $activos,
            'pedidos_recientes' => array_slice($recientes, 0, 5),
        ];
    }
}
