<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Session;

class FastApiService
{
    private string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = env('API_URL', 'http://fastapi:8080');
    }

    // ── Token helpers ──────────────────────────────────────────────────

    /**
     * Retrieve the cached JWT token from session, or obtain a new one.
     *
     * @return string|null
     */
    private function token(): ?string
    {
        return Session::get('api_access_token');
    }

    /**
     * Store a fresh JWT token in session.
     */
    private function setToken(string $token): void
    {
        Session::put('api_access_token', $token);
    }

    /**
     * Clear the stored token (e.g. on logout or 401).
     */
    private function clearToken(): void
    {
        Session::forget('api_access_token');
    }

    /**
     * Authenticate as a client (Laravel customer) and store the JWT.
     *
     * @return array|null  response data or null on failure
     */
    public function authenticateClient(string $email, string $password): ?array
    {
        try {
            $response = Http::asForm()
                ->timeout(10)
                ->post($this->baseUrl . '/v1/auth/login-cliente', [
                    'username' => $email,
                    'password' => $password,
                ]);

            if (! $response->successful()) {
                return null;
            }

            $data = $response->json();
            if (isset($data['data']['access_token'])) {
                $this->setToken($data['data']['access_token']);
            }

            return $data;
        } catch (\Exception $e) {
            return null;
        }
    }

    /**
     * Register a new client (public endpoint – no token needed).
     */
    public function registrarCliente(array $data): ?array
    {
        try {
            $response = Http::asJson()
                ->timeout(10)
                ->post($this->baseUrl . '/v1/clientes/registro', $data);

            if ($response->status() === 422) {
                return ['error' => $response->json('detail', 'Error de validación')];
            }

            return $response->json();
        } catch (\Exception $e) {
            return ['error' => $e->getMessage()];
        }
    }

    // ── HTTP helpers with auto-retry on 401 ────────────────────────────

    private function authHeaders(): array
    {
        $token = $this->token();
        return $token ? ['Authorization' => 'Bearer ' . $token] : [];
    }

    private function retryWithNewToken(callable $callback): ?array
    {
        try {
            return $callback();
        } catch (\Exception $e) {
            // If we got a 401, try to re-authenticate and retry once
            if (isset($e->response) && $e->response->status() === 401) {
                $this->clearToken();
                // The caller's session should have _api_email and _api_password
                if (Session::has('_api_email') && Session::has('_api_password')) {
                    $authResult = $this->authenticateClient(
                        Session::get('_api_email'),
                        Session::get('_api_password')
                    );
                    if ($authResult && isset($authResult['data']['access_token'])) {
                        return $callback();
                    }
                }
            }
            throw $e;
        }
    }

    public function get(string $path, array $params = []): ?array
    {
        return $this->retryWithNewToken(function () use ($path, $params) {
            $response = Http::withHeaders($this->authHeaders())
                ->timeout(10)
                ->get($this->baseUrl . $path, $params);

            $response->throw();
            return $response->json();
        });
    }

    public function post(string $path, array $data): ?array
    {
        return $this->retryWithNewToken(function () use ($path, $data) {
            $response = Http::withHeaders($this->authHeaders())
                ->timeout(10)
                ->post($this->baseUrl . $path, $data);

            if ($response->status() === 422) {
                return ['error' => $response->json('detail', 'Error de validación')];
            }

            $response->throw();
            return $response->json();
        });
    }

    public function put(string $path, array $data): ?array
    {
        return $this->retryWithNewToken(function () use ($path, $data) {
            $response = Http::withHeaders($this->authHeaders())
                ->timeout(10)
                ->put($this->baseUrl . $path, $data);

            $response->throw();
            return $response->json();
        });
    }

    public function delete(string $path): ?array
    {
        return $this->retryWithNewToken(function () use ($path) {
            $response = Http::withHeaders($this->authHeaders())
                ->timeout(10)
                ->delete($this->baseUrl . $path);

            $response->throw();
            return $response->json();
        });
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
        return $this->get('/v1/pedidos/externos/', [
            'cliente_id' => $clienteId,
            'page'       => $page,
            'per_page'   => 20,
        ]);
    }

    public function getPedidoExterno(int $id): ?array
    {
        return $this->get("/v1/pedidos/externos/{$id}");
    }

    public function crearPedidoExterno(int $clienteId, array $items, string $notas = ''): ?array
    {
        $payload = ['cliente_id' => $clienteId, 'items' => $items, 'notas' => $notas];
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
            'total_pedidos'   => $total,
            'pedidos_activos' => $activos,
            'pedidos_recientes' => array_slice($recientes, 0, 5),
        ];
    }
}
