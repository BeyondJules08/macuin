<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class CheckSession
{
    public function handle(Request $request, Closure $next)
    {
        if (!session('cliente')) {
            return redirect('/login')->with('warning', 'Por favor inicia sesión para continuar.');
        }
        return $next($request);
    }
}
