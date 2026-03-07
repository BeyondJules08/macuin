# Guía de Integración Flask ↔ Laravel

## 🎯 Objetivo

Conectar el sistema Flask (personal interno) con Laravel (clientes externos) mediante API REST.

## 🏗️ Arquitectura Propuesta

```
┌─────────────────┐         API REST         ┌─────────────────┐
│  Laravel        │ ←──────────────────────→ │  Flask          │
│  (Clientes)     │    JSON over HTTP        │  (Staff)        │
│                 │                          │                 │
│  • E-commerce   │                          │  • Ventas       │
│  • Pedidos      │                          │  • Almacén      │
│  • Consultas    │                          │  • Logística    │
└─────────────────┘                          └─────────────────┘
        │                                              │
        ▼                                              ▼
   MySQL/MariaDB                                   SQLite/MySQL
   (Clientes)                                      (Inventario)
```

## 📡 Endpoints API Sugeridos

### 1. Consulta de Inventario

**Endpoint**: `GET /api/v1/inventario`

**Ejemplo Flask**:
```python
@app.route('/api/v1/inventario', methods=['GET'])
def api_inventario():
    """API: Obtener inventario disponible"""
    autopartes = db.session.query(Autoparte, Inventario).join(
        Inventario, Autoparte.id == Inventario.autoparte_id
    ).filter(Autoparte.activo == True).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': ap.id,
            'nombre': ap.nombre,
            'descripcion': ap.descripcion,
            'categoria': ap.categoria.nombre,
            'marca': ap.marca,
            'precio': float(ap.precio),
            'stock_disponible': inv.stock_actual,
            'stock_minimo': inv.stock_minimo,
            'disponible': inv.stock_actual > 0
        } for ap, inv in autopartes]
    })
```

**Ejemplo Laravel** (consumir):
```php
// En Laravel Controller
public function getInventario()
{
    $response = Http::get('http://flask-api.local/api/v1/inventario');
    
    if ($response->successful()) {
        $inventario = $response->json()['data'];
        return view('inventario', compact('inventario'));
    }
}
```

### 2. Verificar Disponibilidad

**Endpoint**: `GET /api/v1/inventario/{id}/disponibilidad`

**Ejemplo Flask**:
```python
@app.route('/api/v1/inventario/<int:id>/disponibilidad', methods=['GET'])
def api_verificar_disponibilidad(id):
    """API: Verificar si hay stock disponible"""
    cantidad_solicitada = request.args.get('cantidad', 1, type=int)
    
    autoparte = Autoparte.query.get_or_404(id)
    disponible = autoparte.inventario.stock_actual >= cantidad_solicitada
    
    return jsonify({
        'success': True,
        'autoparte_id': id,
        'cantidad_solicitada': cantidad_solicitada,
        'stock_actual': autoparte.inventario.stock_actual,
        'disponible': disponible
    })
```

**Ejemplo Laravel**:
```php
public function verificarStock($autoparteId, $cantidad)
{
    $url = "http://flask-api.local/api/v1/inventario/{$autoparteId}/disponibilidad";
    $response = Http::get($url, ['cantidad' => $cantidad]);
    
    return $response->json()['disponible'];
}
```

### 3. Crear Pedido desde Laravel

**Endpoint**: `POST /api/v1/pedidos`

**Ejemplo Flask**:
```python
@app.route('/api/v1/pedidos', methods=['POST'])
def api_crear_pedido():
    """API: Crear pedido desde sistema externo"""
    data = request.get_json()
    
    try:
        # Crear pedido
        estado_pendiente = EstadoPedido.query.filter_by(nombre='Pendiente').first()
        usuario_api = Usuario.query.filter_by(email='api@macuin.com').first()
        
        pedido = Pedido(
            usuario_id=usuario_api.id,
            estado_id=estado_pendiente.id,
            total=0
        )
        db.session.add(pedido)
        db.session.flush()
        
        # Agregar detalles
        for item in data['items']:
            autoparte = Autoparte.query.get(item['autoparte_id'])
            
            # Verificar stock
            if autoparte.inventario.stock_actual < item['cantidad']:
                raise Exception(f'Stock insuficiente para {autoparte.nombre}')
            
            # Crear detalle
            detalle = DetallePedido(
                pedido_id=pedido.id,
                autoparte_id=autoparte.id,
                cantidad=item['cantidad'],
                precio_unitario=autoparte.precio
            )
            db.session.add(detalle)
            
            # Descontar inventario
            autoparte.inventario.stock_actual -= item['cantidad']
        
        # Calcular total
        pedido.calcular_total()
        
        # Guardar referencia del pedido externo
        pedido.referencia_externa = data.get('referencia_laravel', None)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pedido_id': pedido.id,
            'total': float(pedido.total),
            'mensaje': 'Pedido creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
```

**Ejemplo Laravel**:
```php
public function crearPedidoFlask($pedidoLaravel)
{
    $items = [];
    foreach ($pedidoLaravel->items as $item) {
        $items[] = [
            'autoparte_id' => $item->autoparte_id,
            'cantidad' => $item->cantidad
        ];
    }
    
    $response = Http::post('http://flask-api.local/api/v1/pedidos', [
        'items' => $items,
        'referencia_laravel' => $pedidoLaravel->id
    ]);
    
    if ($response->successful()) {
        $data = $response->json();
        // Guardar referencia del pedido Flask
        $pedidoLaravel->pedido_flask_id = $data['pedido_id'];
        $pedidoLaravel->save();
        
        return $data;
    }
}
```

### 4. Actualizar Estado de Pedido

**Endpoint**: `PUT /api/v1/pedidos/{id}/estado`

**Ejemplo Flask**:
```python
@app.route('/api/v1/pedidos/<int:id>/estado', methods=['PUT'])
def api_actualizar_estado_pedido(id):
    """API: Actualizar estado de pedido"""
    data = request.get_json()
    
    pedido = Pedido.query.get_or_404(id)
    nuevo_estado = EstadoPedido.query.filter_by(nombre=data['estado']).first()
    
    if not nuevo_estado:
        return jsonify({'success': False, 'error': 'Estado no válido'}), 400
    
    pedido.estado_id = nuevo_estado.id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'pedido_id': pedido.id,
        'estado': nuevo_estado.nombre
    })
```

### 5. Sincronizar Inventario

**Endpoint**: `PUT /api/v1/inventario/{id}`

**Ejemplo Flask**:
```python
@app.route('/api/v1/inventario/<int:id>', methods=['PUT'])
def api_actualizar_inventario(id):
    """API: Actualizar stock de inventario"""
    data = request.get_json()
    
    inventario = Inventario.query.filter_by(autoparte_id=id).first_or_404()
    
    operacion = data.get('operacion', 'establecer')
    cantidad = data.get('cantidad', 0)
    
    if operacion == 'agregar':
        inventario.stock_actual += cantidad
    elif operacion == 'restar':
        if inventario.stock_actual >= cantidad:
            inventario.stock_actual -= cantidad
        else:
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400
    elif operacion == 'establecer':
        inventario.stock_actual = cantidad
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'autoparte_id': id,
        'stock_actual': inventario.stock_actual
    })
```

## 🔐 Autenticación API

### Opción 1: API Key Simple

**Flask**:
```python
from functools import wraps

API_KEY = 'tu-clave-secreta-api'

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'API Key inválida'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/inventario')
@require_api_key
def api_inventario():
    # ...
```

**Laravel**:
```php
$response = Http::withHeaders([
    'X-API-Key' => config('services.flask.api_key')
])->get('http://flask-api.local/api/v1/inventario');
```

### Opción 2: JWT Tokens

**Instalar en Flask**:
```bash
pip install Flask-JWT-Extended
```

**Flask**:
```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)

@app.route('/api/v1/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    # Validar credenciales
    if data['username'] == 'laravel' and data['password'] == 'secret':
        token = create_access_token(identity='laravel-api')
        return jsonify({'access_token': token})
    return jsonify({'error': 'Credenciales inválidas'}), 401

@app.route('/api/v1/inventario')
@jwt_required()
def api_inventario():
    # ...
```

**Laravel**:
```php
// Obtener token
$loginResponse = Http::post('http://flask-api.local/api/v1/auth/login', [
    'username' => 'laravel',
    'password' => config('services.flask.password')
]);

$token = $loginResponse->json()['access_token'];

// Usar token
$response = Http::withToken($token)
    ->get('http://flask-api.local/api/v1/inventario');
```

## 🔄 Webhooks para Sincronización

### Flask notifica a Laravel cuando cambia el inventario

**Flask**:
```python
import requests

LARAVEL_WEBHOOK_URL = 'http://laravel.local/api/webhooks/inventario-actualizado'

def notificar_laravel_inventario(autoparte_id, stock_actual):
    """Notificar a Laravel sobre cambio de inventario"""
    try:
        requests.post(LARAVEL_WEBHOOK_URL, json={
            'autoparte_id': autoparte_id,
            'stock_actual': stock_actual,
            'timestamp': datetime.now().isoformat()
        }, timeout=5)
    except:
        # Log error pero no fallar
        pass

# Usar en actualización de inventario
@app.route('/inventario/<int:id>/actualizar', methods=['POST'])
@login_required
def inventario_update(id):
    # ... lógica de actualización ...
    db.session.commit()
    
    # Notificar a Laravel
    notificar_laravel_inventario(inventario.autoparte_id, inventario.stock_actual)
```

**Laravel**:
```php
// Route
Route::post('/api/webhooks/inventario-actualizado', [WebhookController::class, 'inventarioActualizado']);

// Controller
public function inventarioActualizado(Request $request)
{
    $autoparteId = $request->autoparte_id;
    $stockActual = $request->stock_actual;
    
    // Actualizar en base de datos Laravel
    Autoparte::where('flask_id', $autoparteId)
        ->update(['stock' => $stockActual]);
    
    // Notificar a clientes via broadcasting
    broadcast(new InventarioActualizado($autoparteId, $stockActual));
    
    return response()->json(['success' => true]);
}
```

## 📊 Sincronización de Datos

### Script de Sincronización Periódica (Laravel)

```php
// app/Console/Commands/SincronizarInventario.php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class SincronizarInventario extends Command
{
    protected $signature = 'inventario:sincronizar';
    protected $description = 'Sincronizar inventario con Flask';

    public function handle()
    {
        $this->info('Sincronizando inventario con Flask...');
        
        $response = Http::get('http://flask-api.local/api/v1/inventario');
        
        if ($response->successful()) {
            $inventario = $response->json()['data'];
            
            foreach ($inventario as $item) {
                \App\Models\Autoparte::updateOrCreate(
                    ['flask_id' => $item['id']],
                    [
                        'nombre' => $item['nombre'],
                        'precio' => $item['precio'],
                        'stock' => $item['stock_disponible']
                    ]
                );
            }
            
            $this->info('Sincronización completada: ' . count($inventario) . ' productos');
        } else {
            $this->error('Error al sincronizar');
        }
    }
}
```

**Programar en Laravel**:
```php
// app/Console/Kernel.php
protected function schedule(Schedule $schedule)
{
    $schedule->command('inventario:sincronizar')->everyFifteenMinutes();
}
```

## 🧪 Testing de la API

### Probar con cURL

```bash
# Obtener inventario
curl -X GET http://localhost:5000/api/v1/inventario

# Crear pedido
curl -X POST http://localhost:5000/api/v1/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"autoparte_id": 1, "cantidad": 2},
      {"autoparte_id": 2, "cantidad": 1}
    ]
  }'

# Actualizar stock
curl -X PUT http://localhost:5000/api/v1/inventario/1 \
  -H "Content-Type: application/json" \
  -d '{"operacion": "agregar", "cantidad": 10}'
```

### Probar con Postman

1. Importar colección con endpoints
2. Configurar variables de entorno
3. Ejecutar tests automatizados

## 📝 Ejemplo Completo: Flujo de Pedido

### 1. Cliente hace pedido en Laravel

```php
// Laravel Controller
public function store(PedidoRequest $request)
{
    DB::beginTransaction();
    try {
        // 1. Verificar disponibilidad en Flask
        foreach ($request->items as $item) {
            $disponible = $this->verificarStockFlask(
                $item['autoparte_id'], 
                $item['cantidad']
            );
            
            if (!$disponible) {
                throw new \Exception("Stock insuficiente");
            }
        }
        
        // 2. Crear pedido en Laravel
        $pedido = Pedido::create($request->validated());
        
        // 3. Crear pedido en Flask (reserva inventario)
        $pedidoFlask = $this->crearPedidoFlask($pedido);
        
        // 4. Guardar referencia
        $pedido->pedido_flask_id = $pedidoFlask['pedido_id'];
        $pedido->save();
        
        DB::commit();
        return response()->json($pedido);
    } catch (\Exception $e) {
        DB::rollBack();
        return response()->json(['error' => $e->getMessage()], 400);
    }
}
```

### 2. Flask procesa y descuenta inventario

```python
# Ya implementado en api_crear_pedido()
```

### 3. Logística cambia estado en Flask

```python
# Interface web de Flask
# Usuario de logística cambia estado a "En Camino"
```

### 4. Flask notifica a Laravel (webhook)

```python
def notificar_cambio_estado(pedido):
    requests.post(f'{LARAVEL_URL}/api/webhooks/pedido-estado', json={
        'pedido_flask_id': pedido.id,
        'estado': pedido.estado.nombre
    })
```

### 5. Laravel notifica al cliente

```php
public function pedidoEstadoActualizado(Request $request)
{
    $pedido = Pedido::where('pedido_flask_id', $request->pedido_flask_id)->first();
    $pedido->update(['estado' => $request->estado]);
    
    // Notificar al cliente
    Mail::to($pedido->cliente->email)
        ->send(new PedidoActualizado($pedido));
    
    return response()->json(['success' => true]);
}
```

## 🔒 Seguridad

1. **Usar HTTPS** en producción
2. **Validar API Keys** o tokens
3. **Rate limiting** para prevenir abuso
4. **Validar datos** de entrada
5. **Logs de auditoría** de operaciones API
6. **CORS configurado** correctamente

## 📚 Recursos

- **Flask REST API**: https://flask-restful.readthedocs.io/
- **Laravel HTTP Client**: https://laravel.com/docs/http-client
- **JWT Auth**: https://flask-jwt-extended.readthedocs.io/

---

**Última actualización**: Marzo 2024
