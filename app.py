from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Base de datos simulada con permisos estrictos por Rol
USUARIOS_AUTORIZADOS = {
    "admin@ecomarket.com": {
        "password": "EcoVital2026*",
        "rol": "Administrador del Sistema (Full Access)",
        "pin_2fa": "8492"
    },
    "gerente@ecomarket.com": {
        "password": "Gerente2026*",
        "rol": "Gerente de Sucursal",
        "pin_2fa": "1122"
    },
    "cajero@ecomarket.com": {
        "password": "Cajero2026*",
        "rol": "Cajero / Operador",
        "pin_2fa": "3344"
    }
}

# Bitácora de Auditoría en tiempo real para eventos de seguridad
BITACORA_AUDITORIA = [
    {"id": "LOG-901", "timestamp": "2026-11-12 08:00:15", "usuario": "admin@ecomarket.com", "accion": "Inicio de sesión exitoso con token y biometría"},
    {"id": "LOG-902", "timestamp": "2026-11-12 10:14:32", "usuario": "cajero@ecomarket.com", "accion": "Apertura de turno en Terminal POS 01"},
    {"id": "LOG-903", "timestamp": "2026-11-12 12:30:00", "usuario": "gerente@ecomarket.com", "accion": "Consulta de inventario bajo y sucursales"}
]

# Almacén central de sugerencias del supermercado
BUZON_SUGERENCIAS = [
    {"id": "SUG-01", "remitente": "cajero@ecomarket.com", "tipo": "Reporte de Incidencia Operativa", "mensaje": "Se requiere mantenimiento preventivo en el lector de códigos de barras de la Caja 1."},
    {"id": "SUG-02", "remitente": "gerente@ecomarket.com", "tipo": "Sugerencia de Mejora Ecológica", "mensaje": "Ampliar el stock de productos de cosmética natural para la sucursal de Altamira."}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoMarket Vital - Sistema de Gestión</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-black min-h-screen flex items-center justify-center p-4 text-white font-sans">

    <!-- LOGIN CONTAINER -->
    <div id="login-container" class="w-full max-w-md bg-[#2b3e30] p-8 rounded-3xl shadow-2xl border border-[#4a6b52] relative overflow-hidden flex flex-col justify-between">
        <div>
            <div class="flex flex-col items-center mb-6">
                <div class="w-20 h-20 bg-[#3a5240] rounded-2xl flex items-center justify-center border border-[#5c8266] mb-3 shadow-lg">
                    <i class="fa-solid fa-cart-shopping text-3xl text-[#a3c1ad]"></i>
                </div>
                <h1 class="text-2xl font-black tracking-wider text-[#d0e1d4]">EcoMarket Vital</h1>
                <p class="text-xs text-[#a3c1ad] mt-1 uppercase tracking-widest font-bold">Jean3.1416er.beta</p>
            </div>

            <div id="error-box" class="hidden mb-4 p-3 bg-red-950 border border-red-600 rounded-2xl text-xs text-red-200 flex items-center gap-2 shadow-lg">
                <i class="fa-solid fa-shield-halved text-red-400 text-base"></i>
                <span id="error-msg">Acceso denegado.</span>
            </div>

            <form onsubmit="validarAcceso(event)" class="space-y-4">
                <div class="relative flex items-center">
                    <span class="absolute left-4 text-[#a3c1ad]"><i class="fa-solid fa-envelope text-xs"></i></span>
                    <input type="email" id="email" required placeholder="Correo Corporativo"
                        class="w-full pl-11 pr-4 py-3 bg-[#1e2c21] border border-[#4a6b52] rounded-full text-sm text-white placeholder-[#a3c1ad]/60 focus:outline-none focus:border-[#a3c1ad] transition shadow-inner">
                </div>

                <div class="relative flex items-center">
                    <span class="absolute left-4 text-[#a3c1ad]"><i class="fa-solid fa-lock text-xs"></i></span>
                    <input type="password" id="password" required placeholder="Contraseña de Acceso"
                        class="w-full pl-11 pr-4 py-3 bg-[#1e2c21] border border-[#4a6b52] rounded-full text-sm text-white placeholder-[#a3c1ad]/60 focus:outline-none focus:border-[#a3c1ad] transition shadow-inner">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="relative flex items-center">
                        <select id="rol" class="w-full px-4 py-3 bg-[#1e2c21] border border-[#4a6b52] rounded-full text-xs text-white focus:outline-none focus:border-[#a3c1ad] transition cursor-pointer">
                            <option value="Administrador del Sistema (Full Access)" class="bg-[#1e2c21]">Administrador</option>
                            <option value="Gerente de Sucursal" class="bg-[#1e2c21]">Gerente</option>
                            <option value="Cajero / Operador" class="bg-[#1e2c21]">Cajero</option>
                        </select>
                    </div>
                    <div class="relative flex items-center">
                        <input type="text" id="pin" required maxlength="4" placeholder="Token Único"
                            class="w-full px-4 py-3 bg-[#1e2c21] border border-[#4a6b52] rounded-full text-sm text-center tracking-widest font-mono text-[#a3c1ad] placeholder-[#a3c1ad]/60 focus:outline-none focus:border-[#a3c1ad] transition shadow-inner">
                    </div>
                </div>

                <div class="space-y-2 pt-1 bg-[#1e2c21]/60 p-3.5 rounded-2xl border border-[#4a6b52]/50">
                    <label class="flex items-center space-x-2.5 cursor-pointer">
                        <input type="checkbox" id="biometria" class="w-4 h-4 accent-[#5c8266] rounded">
                        <span class="text-xs text-[#d0e1d4] font-medium"><i class="fa-solid fa-fingerprint text-[#a3c1ad] mr-1"></i> Biometría - OBLIGATORIA </span>
                    </label>
                    <label class="flex items-center space-x-2.5 cursor-pointer">
                        <input type="checkbox" id="polp" checked class="w-4 h-4 accent-[#5c8266] rounded">
                        <span class="text-xs text-[#d0e1d4] font-medium"><i class="fa-solid fa-user-shield text-[#a3c1ad] mr-1"></i>  (Confirmar si no eres un robot )</span>
                    </label>
                </div>

                <button type="submit"
                    class="w-full py-3.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white font-black rounded-full shadow-lg transition duration-200 uppercase tracking-wider text-xs cursor-pointer">
                    Verificar e Ingresar
                </button>
            </form>
        </div>

        <div class="mt-6 pt-3 border-t border-[#4a6b52]/90 text-center">
            <p class="text-[11px] text-[#a3c1ad] font-bold uppercase tracking-widest"><i class="fa-solid fa-shield-halved mr-9"></i> Portal de Acesso — EcoMarket Vital </p>
        </div>
    </div>

    <!-- PANEL ANALÍTICO Y DE NEGOCIO -->
    <div id="dashboard-container" class="hidden w-full max-w-6xl bg-[#1a241c] border border-[#3a5240] p-6 md:p-8 rounded-3xl shadow-2xl my-6">
        
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#3a5240] pb-5 mb-6 gap-4">
            <div>
                <div class="flex flex-wrap items-center gap-2 mb-2">
                    <span id="badge-rol" class="px-3.5 py-1 bg-[#2b3e30] border border-[#4a6b52] text-[#a3c1ad] text-xs font-bold rounded-full"></span>
                </div>
                <h2 class="text-2xl font-black text-white" id="titulo-panel">Panel de Control - EcoMarket Vital</h2>
                <p class="text-xs text-[#a3c1ad]" id="sub-panel">Gestión Integral de Catálogos y Vistas SQL en Supabase dentro de nuestro sistema Jean3.1416er.beta</p>
            </div>
            <div class="flex items-center gap-2">
                <div id="admin-acciones-extra" class="hidden flex items-center gap-2">
                    <button onclick="abrirBitacora()" class="px-3 py-2 bg-[#3a5240] hover:bg-[#4a6b52] text-[#a3c1ad] text-xs font-bold rounded-xl shadow transition cursor-pointer flex items-center gap-1.5">
                        <i class="fa-solid fa-shield-cat"></i> Bitácora
                    </button>
                </div>
                <button onclick="abrirBuzon()" id="btn-buzon" class="px-4 py-2 bg-[#3a5240] hover:bg-[#4a6b52] text-white text-xs font-bold rounded-xl shadow transition cursor-pointer flex items-center gap-1.5">
                    <i class="fa-solid fa-comment-dots"></i> <span id="txt-btn-buzon">Buzón</span>
                </button>
                <button onclick="cerrarSesion()" class="px-4 py-2 bg-rose-800 hover:bg-rose-700 text-white text-xs font-bold rounded-xl shadow transition cursor-pointer flex items-center gap-1.5">
                    <i class="fa-solid fa-power-off"></i> Salir
                </button>
            </div>
        </div>

        <!-- PILARES Y CATÁLOGOS DEL NEGOCIO (Filtrados por Rol / PoLP) -->
        <div class="mb-8 bg-[#2b3e30] border border-[#4a6b52] p-5 rounded-2xl shadow-xl">
            <div class="flex justify-between items-center mb-3">
                <h3 class="font-bold text-sm text-[#a3c1ad]"><i class="fa-solid fa-boxes-stacked mr-2"></i> Pilares y Catálogos del Negocio</h3>
                <div id="cajero-acciones-extra" class="hidden">
                    <button onclick="abrirArqueoCaja()" class="px-3 py-1.5 bg-[#1e2c21] hover:bg-[#3a5240] border border-[#4a6b52] text-[#a3c1ad] text-xs font-bold rounded-xl shadow transition cursor-pointer flex items-center gap-1">
                        <i class="fa-solid fa-cash-register"></i> Arqueo / Cierre de Turno
                    </button>
                </div>
            </div>
            <div id="grid-pilares" class="grid grid-cols-2 md:grid-cols-4 gap-3"></div>
        </div>

        <!-- MÓDULO INTERACTIVO DE CAJA (POS) CON PRODUCTOS -->
        <div id="modulo-cajero" class="hidden mb-6 bg-[#2b3e30] border border-[#4a6b52] p-5 rounded-2xl shadow-xl">
            <h3 class="font-bold text-sm text-[#a3c1ad] mb-3"><i class="fa-solid fa-cash-register mr-2"></i> Venta al público CAJA POS</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                <div>
                    <label class="block text-xs font-bold text-[#d0e1d4] mb-1">Seleccionar Producto</label>
                    <select id="pos-producto" class="w-full px-3 py-2.5 bg-[#1e2c21] border border-[#4a6b52] rounded-xl text-xs text-white focus:outline-none focus:border-[#a3c1ad]">
                        <option value="Panela Orgánica Artesanal|$3.50">Panela Orgánica Artesanal ($3.50)</option>
                        <option value="Aceite de Oliva 500ml|$14.50">Aceite de Oliva 500ml ($14.50)</option>
                        <option value="Avena Integral 1kg|$2.90">Avena Integral 1kg ($2.90)</option>
                        <option value="Té Verde Matcha 200g|$9.00">Té Verde Matcha 200g ($9.00)</option>
                        <option value="Azúcar de Coco Orgánica|$5.20">Azúcar de Coco Orgánica ($5.20)</option>
                        <option value="Miel de Abeja Pura 500g|$7.80">Miel de Abeja Pura 500g ($7.80)</option>
                        <option value="Jabón Orgánico de Avena|$4.00">Jabón Orgánico de Avena ($4.00)</option>
                        <option value="Shampoo Sólido Natural|$6.50">Shampoo Sólido Natural ($6.50)</option>
                        <option value="Granola con Nuez 500g|$6.00">Granola con Nuez 500g ($6.00)</option>
                        <option value="Protector Solar Botánico|$12.00">Protector Solar Botánico ($12.00)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-[#d0e1d4] mb-1">Cantidad</label>
                    <input type="number" id="pos-cantidad" value="1" min="1" max="50" class="w-full px-3 py-2.5 bg-[#1e2c21] border border-[#4a6b52] rounded-xl text-xs text-white focus:outline-none focus:border-[#a3c1ad]">
                </div>
                <div>
                    <label class="block text-xs font-bold text-[#d0e1d4] mb-1">Método de Pago</label>
                    <select id="pos-pago" class="w-full px-3 py-2.5 bg-[#1e2c21] border border-[#4a6b52] rounded-xl text-xs text-white focus:outline-none focus:border-[#a3c1ad]">
                        <option value="Tarjeta de Débito">Tarjeta de Débito</option>
                        <option value="Pago Móvil">Pago Móvil</option>
                        <option value="Zelle / Divisas">Zelle / Divisas</option>
                        <option value="Efectivo USD">Efectivo USD</option>
                    </select>
                </div>
                <div>
                    <button onclick="registrarVentaPOS()" class="w-full py-2.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white font-black text-xs rounded-xl shadow transition cursor-pointer">
                        Procesar y Facturar
                    </button>
                </div>
            </div>
            <div id="pos-resultado" class="mt-3 hidden p-3 bg-[#1e2c21] border border-[#4a6b52] rounded-xl text-xs text-[#a3c1ad]"></div>
        </div>

        <!-- CONTENEDOR DE CONSULTAS SQL -->
        <h3 class="text-sm font-bold text-[#a3c1ad] mb-3 uppercase tracking-wider"><i class="fa-solid fa-database mr-1"></i> Módulo de Consultas SQL Oficiales (10 / 10)</h3>
        <div id="grid-consultas" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </div>

    <!-- MODAL DE BITÁCORA DE AUDITORÍA -->
    <div id="modal-bitacora" class="hidden fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50">
        <div class="bg-[#1a241c] border border-[#4a6b52] w-full max-w-3xl rounded-3xl p-6 shadow-2xl text-white">
            <div class="flex justify-between items-center border-b border-[#3a5240] pb-3 mb-4">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-lg bg-[#2b3e30] flex items-center justify-center text-[#a3c1ad]"><i class="fa-solid fa-shield-cat"></i></div>
                    <h3 class="text-base font-bold text-white">Bitácora de Auditoría y Seguridad</h3>
                </div>
                <button onclick="document.getElementById('modal-bitacora').classList.add('hidden')" class="text-slate-400 hover:text-white text-lg font-bold px-2.5 py-1 bg-[#2b3e30] rounded-xl">&times;</button>
            </div>
            <p class="text-xs text-slate-300 mb-4">Registro inalterable de eventos del sistema y trazas de seguridad por rol.</p>
            <div class="overflow-x-auto max-h-72 rounded-2xl border border-[#3a5240]">
                <table class="w-full text-left text-xs">
                    <thead class="bg-[#2b3e30] text-[#a3c1ad] uppercase font-bold">
                        <tr>
                            <th class="px-4 py-3">ID Log</th>
                            <th class="px-4 py-3">Fecha y Hora</th>
                            <th class="px-4 py-3">Usuario</th>
                            <th class="px-4 py-3">Acción Registrada</th>
                        </tr>
                    </thead>
                    <tbody id="tabla-bitacora-cuerpo" class="divide-y divide-[#3a5240] bg-black/50"></tbody>
                </table>
            </div>
            <div class="mt-5 flex justify-end">
                <button onclick="document.getElementById('modal-bitacora').classList.add('hidden')" class="px-5 py-2.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white text-xs font-bold rounded-xl cursor-pointer">Cerrar Bitácora</button>
            </div>
        </div>
    </div>

    <!-- MODAL DE BUZÓN DE SUGERENCIAS (Dinámico según el rol) -->
    <div id="modal-buzon" class="hidden fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50">
        <div class="bg-[#1a241c] border border-[#4a6b52] w-full max-w-2xl rounded-3xl p-6 shadow-2xl text-white relative">
            <div class="flex justify-between items-center border-b border-[#3a5240] pb-3 mb-4">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-lg bg-[#2b3e30] flex items-center justify-center text-[#a3c1ad]"><i class="fa-solid fa-comments"></i></div>
                    <h3 id="buzon-titulo-modal" class="text-base font-bold text-white">Buzón de Sugerencias</h3>
                </div>
                <button onclick="document.getElementById('modal-buzon').classList.add('hidden')" class="text-slate-400 hover:text-white text-lg font-bold px-2.5 py-1 bg-[#2b3e30] rounded-xl">&times;</button>
            </div>

            <!-- VISTA PARA CAJERO Y GERENTE (Enviar sugerencia) -->
            <div id="buzon-vista-enviar" class="space-y-3">
                <p class="text-xs text-slate-300 mb-2">Envía tus propuestas de optimización ecológica o reportes de incidencia operativa para la administración.</p>
                <div>
                    <label class="block text-xs font-bold text-[#a3c1ad] mb-1">TIPO DE SOLICITUD</label>
                    <select id="sug-tipo" class="w-full px-3 py-2 bg-[#1e2c21] border border-[#4a6b52] rounded-xl text-xs text-white">
                        <option value="Sugerencia de Mejora Ecológica">Sugerencia de Mejora Ecológica</option>
                        <option value="Optimización de Base de Datos / SQL">Optimización de Base de Datos / SQL</option>
                        <option value="Reporte de Incidencia Operativa">Reporte de Incidencia Operativa</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-[#a3c1ad] mb-1">DETALLE DEL MENSAJE</label>
                    <textarea id="sug-texto" rows="4" placeholder="Escribe aquí tu sugerencia o propuesta..." class="w-full px-3 py-2 bg-[#1e2c21] border border-[#4a6b52] rounded-xl text-xs text-white focus:outline-none focus:border-[#a3c1ad]"></textarea>
                </div>
                <button onclick="enviarSugerencia()" class="w-full py-3 bg-[#4a6b52] hover:bg-[#5c8266] text-white font-black text-xs rounded-xl shadow cursor-pointer transition">
                    Enviar Sugerencia al Sistema
                </button>
                <div id="sug-alerta" class="hidden p-2.5 bg-[#2b3e30] border border-[#4a6b52] rounded-xl text-xs text-[#a3c1ad] text-center font-bold">
                    ✔ ¡Sugerencia registrada con éxito y enviada a la administración!
                </div>
            </div>

            <!-- VISTA PARA ADMINISTRADOR (Bandeja de entrada con sugerencias de cajeros/gerentes) -->
            <div id="buzon-vista-admin" class="hidden space-y-3">
                <p class="text-xs text-slate-300 mb-2">Bandeja de propuestas y reportes enviados por el personal de sucursales:</p>
                <div class="overflow-x-auto max-h-72 rounded-2xl border border-[#3a5240]">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-[#2b3e30] text-[#a3c1ad] uppercase font-bold">
                            <tr>
                                <th class="px-4 py-3">Remitente</th>
                                <th class="px-4 py-3">Tipo de Solicitud</th>
                                <th class="px-4 py-3">Mensaje / Detalle</th>
                            </tr>
                        </thead>
                        <tbody id="tabla-buzon-admin" class="divide-y divide-[#3a5240] bg-black/50"></tbody>
                    </table>
                </div>
                <div class="mt-4 flex justify-end">
                    <button onclick="document.getElementById('modal-buzon').classList.add('hidden')" class="px-5 py-2.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white text-xs font-bold rounded-xl cursor-pointer">Cerrar Bandeja</button>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL DE TICKET FISCAL / FACTURA CON QR -->
    <div id="modal-ticket" class="hidden fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50">
        <div class="bg-[#1a241c] border border-[#4a6b52] w-full max-w-sm rounded-3xl p-6 shadow-2xl text-white relative font-mono">
            <div class="text-center border-b border-dashed border-[#4a6b52] pb-4 mb-3">
                <h3 class="text-sm font-bold text-[#a3c1ad]">ECOMMARKET VITAL, C.A.</h3>
                <p class="text-[10px] text-slate-300">RIF: J-50293812-4 | Charallave, Edo. Miranda</p>
                <p class="text-[10px] text-[#a3c1ad] mt-1 font-bold">COMPROBANTE FISCAL DIGITAL</p>
            </div>
            <div id="ticket-contenido" class="text-xs space-y-1.5 text-slate-200"></div>
            <div class="mt-4 pt-3 border-t border-dashed border-[#4a6b52] flex flex-col items-center">
                <div class="bg-white p-2 rounded-xl mb-2">
                    <i class="fa-solid fa-qrcode text-black text-4xl"></i>
                </div>
                <p class="text-[9px] text-[#a3c1ad]">Escanea para ver factura en Supabase</p>
            </div>
            <div class="mt-5">
                <button onclick="document.getElementById('modal-ticket').classList.add('hidden')" class="w-full py-2.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white font-bold text-xs rounded-xl shadow cursor-pointer font-sans">
                    Cerrar Ticket e Imprimir
                </button>
            </div>
        </div>
    </div>

    <!-- MODAL DE ARQUEO / CIERRE DE CAJA -->
    <div id="modal-arqueo" class="hidden fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50">
        <div class="bg-[#1a241c] border border-[#4a6b52] w-full max-w-md rounded-3xl p-6 shadow-2xl text-white">
            <div class="flex justify-between items-center border-b border-[#3a5240] pb-3 mb-4">
                <h3 class="text-base font-bold text-[#a3c1ad]"><i class="fa-solid fa-cash-register mr-2"></i> Arqueo de Caja y Cierre de Turno</h3>
                <button onclick="document.getElementById('modal-arqueo').classList.add('hidden')" class="text-slate-400 hover:text-white text-lg font-bold px-2.5 py-1 bg-[#2b3e30] rounded-xl">&times;</button>
            </div>
            <div id="arqueo-cuerpo" class="space-y-3 text-xs text-slate-200"></div>
            <div class="mt-5">
                <button onclick="document.getElementById('modal-arqueo').classList.add('hidden')" class="w-full py-2.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white font-bold text-xs rounded-xl shadow cursor-pointer">
                    Aceptar y Registrar Cierre
                </button>
            </div>
        </div>
    </div>

    <script>
        const consultasData = {
            'negocio_catalogo': {
                titulo: "Catálogo de Productos", tipo: "Tabla: productos", desc: "Inventario oficial de productos ecológicos y sustentables.",
                columnas: ["ID", "Nombre del Producto", "Categoría", "Precio Unitario", "Stock"],
                filas: [
                    ["P-101", "Panela Orgánica Artesanal", "Alimentos", "$3.50", "4 un."],
                    ["P-102", "Aceite de Oliva 500ml", "Alimentos", "$14.50", "3 un."],
                    ["P-103", "Avena Integral 1kg", "Alimentos", "$2.90", "5 un."],
                    ["P-104", "Té Verde Matcha 200g", "Bebidas", "$9.00", "2 un."],
                    ["P-105", "Azúcar de Coco Orgánica", "Alimentos", "$5.20", "4 un."],
                    ["P-106", "Miel de Abeja Pura 500g", "Alimentos", "$7.80", "3 un."],
                    ["P-107", "Jabón Orgánico de Avena", "Cosmética", "$4.00", "15 un."],
                    ["P-108", "Shampoo Sólido Natural", "Cosmética", "$6.50", "12 un."],
                    ["P-109", "Granola con Nuez 500g", "Alimentos", "$6.00", "8 un."],
                    ["P-110", "Protector Solar Botánico", "Cosmética", "$12.00", "10 un."]
                ]
            },
            'negocio_fidelidad': {
                titulo: "Clientes en Programa de Fidelidad", tipo: "Tabla: clientes", desc: "Clientes registrados con membresía verde activa y puntos acumulados.",
                columnas: ["ID Cliente", "Nombre completo", "Correo", "Nivel Fidelidad", "Puntos Eco"],
                filas: [
                    ["C-301", "Mariana Gómez", "mariana.g@gmail.com", "VIP Sustentable", "1,450 pts"],
                    ["C-302", "Carlos Mendoza", "carlos.m@hotmail.com", "Oro Verde", "980 pts"],
                    ["C-303", "Sofía Valera", "sofia.valera@outlook.com", "Platino", "1,120 pts"],
                    ["C-304", "Daniela Briceño", "dbriceno@yahoo.com", "VIP Sustentable", "1,600 pts"],
                    ["C-305", "Alejandro Rivas", "arivas99@gmail.com", "Oro Verde", "850 pts"],
                    ["C-306", "Gabriel Soto", "gsoto@gmail.com", "Platino", "920 pts"],
                    ["C-307", "Valentina Pérez", "vperez@outlook.com", "Bronce Eco", "410 pts"],
                    ["C-308", "José Hernández", "jhernandez@gmail.com", "Oro Verde", "790 pts"],
                    ["C-309", "Lucía Morales", "lmorales@hotmail.com", "VIP Sustentable", "1,340 pts"],
                    ["C-310", "Ricardo Silva", "rsilva@gmail.com", "Platino", "880 pts"]
                ]
            },
            'negocio_departamentos': {
                titulo: "Empleados por Departamento", tipo: "Tabla: empleados", desc: "Distribución del personal por departamentos y sucursales.",
                columnas: ["ID Empleado", "Nombre y Apellido", "Departamento", "Cargo", "Sucursal Asignada"],
                filas: [
                    ["EMP-01", "Jeanpier Ledezma", "Tecnología / Sistemas", "Desarrollador Full-Stack", "Charallave"],
                    ["EMP-02", "Alejandro Rivas", "Logística y Almacén", "Encargado de Inventario", "Caracas Centro"],
                    ["EMP-03", "Valeria Sucre", "Atención al Cliente", "Especialista Fidelidad", "Altamira"],
                    ["EMP-04", "Marcos Pérez", "Caja y Operaciones", "Cajero Principal", "Maracay"],
                    ["EMP-05", "Elena Rojas", "Administración", "Contadora General", "Valencia"],
                    ["EMP-06", "Tomás Bolívar", "Ventas", "Asesor Comercial", "Barquisimeto"],
                    ["EMP-07", "Carmen Yánez", "Inventario", "Auditora de Stock", "Charallave"],
                    ["EMP-08", "Luis Blanco", "Seguridad", "Oficial de Protección", "Caracas Centro"],
                    ["EMP-09", "Ana Castillo", "Marketing", "Gerente de Marca", "Altamira"],
                    ["EMP-10", "Pedro Infante", "Mantenimiento", "Técnico Electromecánico", "Valencia"]
                ]
            },
            'negocio_historial': {
                titulo: "Registro Histórico de Ventas", tipo: "Tabla: ventas", desc: "Historial completo y detallado de transacciones históricas.",
                columnas: ["ID Venta", "Fecha y Hora", "Cliente", "Sucursal", "Total Venta ($)"],
                filas: [
                    ["V-5091", "2026-11-12 16:40", "Mariana Gómez", "Charallave", "$45.50"],
                    ["V-5090", "2026-11-12 15:20", "Carlos Mendoza", "Caracas Centro", "$28.00"],
                    ["V-5089", "2026-11-11 14:10", "Sofía Valera", "Altamira", "$62.30"],
                    ["V-5088", "2026-11-11 11:05", "Daniela Briceño", "Valencia", "$19.50"],
                    ["V-5087", "2026-11-10 17:30", "Alejandro Rivas", "Maracay", "$34.20"],
                    ["V-5086", "2026-11-10 12:15", "Gabriel Soto", "Barquisimeto", "$51.00"],
                    ["V-5085", "2026-11-09 10:40", "Valentina Pérez", "Charallave", "$22.80"],
                    ["V-5084", "2026-11-09 09:12", "José Hernández", "Caracas Centro", "$88.40"],
                    ["V-5083", "2026-11-08 18:50", "Lucía Morales", "Altamira", "$41.00"],
                    ["V-5082", "2026-11-08 16:00", "Ricardo Silva", "Valencia", "$30.50"]
                ]
            },
            'v_01_inventario_bajo': {
                titulo: "Inventario Bajo", tipo: "Intermedia", desc: "Productos con stock inferior al promedio general.",
                columnas: ["ID", "Producto", "Stock Actual", "Promedio Mercado"],
                filas: [
                    ["P-101", "Panela Orgánica Artesanal", "4 un.", "18 un."],
                    ["P-102", "Aceite de Oliva 500ml", "3 un.", "18 un."],
                    ["P-103", "Avena Integral 1kg", "5 un.", "18 un."],
                    ["P-104", "Té Verde Matcha 200g", "2 un.", "18 un."],
                    ["P-105", "Azúcar de Coco Orgánica", "4 un.", "18 un."],
                    ["P-106", "Miel de Abeja Pura 500g", "3 un.", "18 un."],
                    ["P-107", "Harina de Trigo Integral", "5 un.", "18 un."],
                    ["P-108", "Chocolate Oscuro 70%", "1 un.", "18 un."],
                    ["P-109", "Granola Artesanal con Nuez", "4 un.", "18 un."],
                    ["P-110", "Vinagre de Manzana Orgánico", "3 un.", "18 un."]
                ]
            },
            'v_02_ventas_metodo_pago': {
                titulo: "Ventas por Método de Pago", tipo: "Intermedia", desc: "Conteo y recaudación por método de pago.",
                columnas: ["Método de Pago", "Transacciones", "Monto Recaudado"],
                filas: [
                    ["Tarjeta Débito Nacional", "142", "$4,850.20"],
                    ["Pago Móvil Interbancario", "98", "$2,140.00"],
                    ["Zelle / Divisas", "65", "$3,920.50"],
                    ["Efectivo USD", "34", "$1,100.00"],
                    ["Tarjeta de Crédito Internacional", "22", "$1,450.00"],
                    ["Transferencia Bancaria", "18", "$890.00"],
                    ["Biopago BDV", "45", "$950.00"],
                    ["Criptomonedas (USDT)", "12", "$1,200.00"],
                    ["Efectivo Bolívares", "50", "$320.00"],
                    ["Crédito Cashea", "30", "$1,800.00"]
                ]
            },
            'v_03_facturacion_cliente': {
                titulo: "Facturación por Cliente", tipo: "INNER JOIN 1", desc: "Nombre, correo y total histórico gastado.",
                columnas: ["Cliente", "Correo Electrónico", "Total Histórico"],
                filas: [
                    ["Mariana Gómez", "mariana.g@gmail.com", "$1,245.00"],
                    ["Carlos Mendoza", "carlos.m@hotmail.com", "$980.50"],
                    ["Sofía Valera", "sofia.valera@outlook.com", "$850.00"],
                    ["Alejandro Rivas", "arivas99@gmail.com", "$740.20"],
                    ["Daniela Briceño", "dbriceno@yahoo.com", "$1,120.00"],
                    ["Gabriel Soto", "gsoto@gmail.com", "$650.00"],
                    ["Valentina Pérez", "vperez@outlook.com", "$910.00"],
                    ["José Hernández", "jhernandez@gmail.com", "$830.40"],
                    ["Lucía Morales", "lmorales@hotmail.com", "$1,050.00"],
                    ["Ricardo Silva", "rsilva@gmail.com", "$790.00"]
                ]
            },
            'v_04_ventas_sucursal': {
                titulo: "Ventas por Sucursal", tipo: "INNER JOIN 2", desc: "Sucursal, ciudad y productos vendidos.",
                columnas: ["Sucursal", "Ciudad", "Unidades Vendidas"],
                filas: [
                    ["Sucursal Centro Los Chaguaramos", "Caracas", "1,420 un."],
                    ["Sucursal Valles del Tuy", "Charallave", "980 un."],
                    ["Sucursal Este Altamira", "Caracas", "1,150 un."],
                    ["Sucursal Las Delicias", "Maracay", "890 un."],
                    ["Sucursal El Viñedo", "Valencia", "1,310 un."],
                    ["Sucursal Barquisimeto Este", "Barquisimeto", "760 un."],
                    ["Sucursal Puerto La Cruz", "Anzoátegui", "640 un."],
                    ["Sucursal San Cristóbal", "Táchira", "590 un."],
                    ["Sucursal Margarita", "Nueva Esparta", "820 un."],
                    ["Sucursal Guatire Plaza", "Miranda", "910 un."]
                ]
            },
            'v_05_empleados_sucursal': {
                titulo: "Empleados y Sucursales", tipo: "INNER JOIN 3", desc: "Nombres, departamento, salario y sucursal.",
                columnas: ["Empleado", "Departamento", "Salario", "Sucursal"],
                filas: [
                    ["Jeanpier Ledezma", "Tecnología / Sistemas", "$850.00", "Charallave"],
                    ["Alejandro Rivas", "Logística y Almacén", "$600.00", "Caracas"],
                    ["Valeria Sucre", "Atención al Cliente", "$550.00", "Altamira"],
                    ["Marcos Pérez", "Caja y Operaciones", "$480.00", "Maracay"],
                    ["Elena Rojas", "Administración", "$750.00", "Valencia"],
                    ["Tomás Bolívar", "Ventas", "$500.00", "Barquisimeto"],
                    ["Carmen Yánez", "Inventario", "$520.00", "Charallave"],
                    ["Luis Blanco", "Seguridad", "$450.00", "Caracas"],
                    ["Ana Castillo", "Marketing", "$680.00", "Altamira"],
                    ["Pedro Infante", "Mantenimiento", "$400.00", "Valencia"]
                ]
            },
            'v_06_transacciones_recientes': {
                titulo: "Detalle de Transacciones", tipo: "INNER JOIN 4", desc: "ID venta, fecha, producto y unidades.",
                columnas: ["ID Venta", "Fecha", "Producto", "Cantidad"],
                filas: [
                    ["V-5091", "2026-11-12", "Panela Orgánica Artesanal", "3 un."],
                    ["V-5090", "2026-11-12", "Café Gourmet Sombra", "2 un."],
                    ["V-5089", "2026-11-11", "Leche de Almendras 1L", "4 un."],
                    ["V-5088", "2026-11-11", "Aceite de Oliva 500ml", "1 un."],
                    ["V-5087", "2026-11-10", "Avena Integral 1kg", "5 un."],
                    ["V-5086", "2026-11-10", "Té Verde Matcha", "2 un."],
                    ["V-5085", "2026-11-09", "Azúcar de Coco", "3 un."],
                    ["V-5084", "2026-11-09", "Miel de Abeja Pura", "2 un."],
                    ["V-5083", "2026-11-08", "Granola Artesanal", "4 un."],
                    ["V-5082", "2026-11-08", "Chocolate Oscuro 70%", "6 un."]
                ]
            },
            'v_07_ranking_empleados': {
                titulo: "Ranking de Empleados", tipo: "Avanzada RANK()", desc: "Posición salarial dentro de cada departamento.",
                columnas: ["Departamento", "Empleado", "Salario", "Rank"],
                filas: [
                    ["Tecnología", "Jeanpier Ledezma", "$850.00", "1"],
                    ["Administración", "Elena Rojas", "$750.00", "1"],
                    ["Marketing", "Ana Castillo", "$680.00", "1"],
                    ["Logística", "Alejandro Rivas", "$600.00", "1"],
                    ["Atención Cliente", "Valeria Sucre", "$550.00", "1"],
                    ["Inventario", "Carmen Yánez", "$520.00", "1"],
                    ["Ventas", "Tomás Bolívar", "$500.00", "1"],
                    ["Operaciones", "Marcos Pérez", "$480.00", "1"],
                    ["Seguridad", "Luis Blanco", "$450.00", "1"],
                    ["Mantenimiento", "Pedro Infante", "$400.00", "1"]
                ]
            },
            'v_08_compra_cruzada': {
                titulo: "Compra Cruzada", tipo: "Subconsulta", desc: "Clientes de 'Cosmética' que nunca compraron 'Alimentos'.",
                columnas: ["ID Cliente", "Nombre", "Categoría Comprada", "Exclusión"],
                filas: [
                    ["C-304", "Daniela Briceño", "Cosmética Natural", "Sin Alimentos"],
                    ["C-412", "Gabriel Soto", "Cuidado Capilar Orgánico", "Sin Alimentos"],
                    ["C-519", "Andrea Meléndez", "Jabón Orgánico de Avena", "Sin Alimentos"],
                    ["C-621", "Ricardo Montilla", "Aceites Esenciales", "Sin Alimentos"],
                    ["C-733", "Paola Romer", "Desodorante Ecológico", "Sin Alimentos"],
                    ["C-801", "Esteban Quintero", "Protector Solar Botánico", "Sin Alimentos"],
                    ["C-845", "Natalia Noguera", "Crema Facial Orgánica", "Sin Alimentos"],
                    ["C-912", "Héctor Lugo", "Shampoo Sólido Natural", "Sin Alimentos"],
                    ["C-950", "Patricia Rivas", "Bálsamo Labial Orgánico", "Sin Alimentos"],
                    ["C-998", "Samuel Duarte", "Exfoliante de Café", "Sin Alimentos"]
                ]
            },
            'v_09_auditoria_crecimiento': {
                titulo: "Auditoría de Crecimiento", tipo: "Avanzada CTE", desc: "Ventas mensuales y % de crecimiento vs mes anterior.",
                columnas: ["Mes", "Ventas Totales", "Mes Anterior", "% Crecimiento"],
                filas: [
                    ["Noviembre 2026", "$16,400.00", "$14,200.00", "+15.49%"],
                    ["Octubre 2026", "$14,200.00", "$12,100.00", "+17.35%"],
                    ["Septiembre 2026", "$12,100.00", "$11,000.00", "+10.00%"],
                    ["Agosto 2026", "$11,000.00", "$9,800.00", "+12.24%"],
                    ["Julio 2026", "$9,800.00", "$10,500.00", "-6.67%"],
                    ["Junio 2026", "$10,500.00", "$9,200.00", "+14.13%"],
                    ["Mayo 2026", "$9,200.00", "$8,900.00", "+3.37%"],
                    ["Abril 2026", "$8,900.00", "$8,100.00", "+9.88%"],
                    ["Marzo 2026", "$8,100.00", "$7,500.00", "+8.00%"],
                    ["Febrero 2026", "$7,500.00", "$7,000.00", "+7.14%"]
                ]
            },
            'v_10_super_compradores': {
                titulo: "Súper Compradores", tipo: "Agregación HAVING", desc: "Clientes con gasto superior al promedio general.",
                columnas: ["Cliente", "Gasto Total", "Promedio General", "Estado"],
                filas: [
                    ["Mariana Gómez", "$1,245.00", "$612.00", "SÚPER COMPRADOR"],
                    ["Daniela Briceño", "$1,120.00", "$612.00", "SÚPER COMPRADOR"],
                    ["Lucía Morales", "$1,050.00", "$612.00", "SÚPER COMPRADOR"],
                    ["Carlos Mendoza", "$980.50", "$612.00", "SÚPER COMPRADOR"],
                    ["Valentina Pérez", "$910.00", "$612.00", "SÚPER COMPRADOR"],
                    ["Sofía Valera", "$850.00", "$612.00", "SÚPER COMPRADOR"],
                    ["José Hernández", "$830.40", "$612.00", "SÚPER COMPRADOR"],
                    ["Ricardo Silva", "$790.00", "$612.00", "SÚPER COMPRADOR"],
                    ["Alejandro Rivas", "$740.20", "$612.00", "SÚPER COMPRADOR"],
                    ["Gabriel Soto", "$650.00", "$612.00", "SÚPER COMPRADOR"]
                ]
            }
        };

        let bitacoraLogs = [
            { id: "LOG-901", fecha: "2026-11-12 08:00", usuario: "admin@ecomarket.com", accion: "Inicio de sesión exitoso con token y biometría" },
            { id: "LOG-902", fecha: "2026-11-12 10:14", usuario: "cajero@ecomarket.com", accion: "Apertura de turno en Terminal POS 01" },
            { id: "LOG-903", fecha: "2026-11-12 12:30", usuario: "gerente@ecomarket.com", accion: "Consulta de inventario bajo y sucursales" }
        ];

        let buzonMensajes = [
            { remitente: "cajero@ecomarket.com", tipo: "Reporte de Incidencia Operativa", mensaje: "Se requiere mantenimiento preventivo en el lector de códigos de barras de la Caja 1." },
            { remitente: "gerente@ecomarket.com", tipo: "Sugerencia de Mejora Ecológica", mensaje: "Ampliar el stock de productos de cosmética natural para la sucursal de Altamira." }
        ];

        let rolActualGlobal = "";
        let usuarioActualGlobal = "";

        async function validarAcceso(e) {
            e.preventDefault();
            const errorBox = document.getElementById('error-box');
            const errorMsg = document.getElementById('error-msg');
            errorBox.classList.add('hidden');

            usuarioActualGlobal = document.getElementById('email').value.trim();
            rolActualGlobal = document.getElementById('rol').value;

            const payload = {
                email: usuarioActualGlobal,
                password: document.getElementById('password').value,
                rol: rolActualGlobal,
                pin: document.getElementById('pin').value.trim(),
                biometria: document.getElementById('biometria').checked
            };

            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (!res.ok) {
                errorMsg.innerText = data.mensaje;
                errorBox.classList.remove('hidden');
                return;
            }

            bitacoraLogs.unshift({
                id: "LOG-" + Math.floor(100 + Math.random() * 900),
                fecha: new Date().toISOString().replace('T', ' ').substring(0, 16),
                usuario: usuarioActualGlobal,
                accion: `Inicio de sesión exitoso en rol: ${rolActualGlobal}`
            });

            configurarPanelPorRol(rolActualGlobal);

            document.getElementById('badge-rol').innerText = "Rol: " + data.rol;
            document.getElementById('login-container').classList.add('hidden');
            document.getElementById('dashboard-container').classList.remove('hidden');
        }

        function configurarPanelPorRol(rol) {
            const gridConsultas = document.getElementById('grid-consultas');
            const gridPilares = document.getElementById('grid-pilares');
            const modCajero = document.getElementById('modulo-cajero');
            const cajeroAccionesExtra = document.getElementById('cajero-acciones-extra');
            const adminAccionesExtra = document.getElementById('admin-acciones-extra');
            const txtBtnBuzon = document.getElementById('txt-btn-buzon');
            
            gridConsultas.innerHTML = "";
            gridPilares.innerHTML = "";

            let keysConsultas = [];
            let pilaresPermitidos = [];

            if (rol.includes("Cajero")) {
                document.getElementById('titulo-panel').innerText = "Terminal de Caja POS - EcoMarket Vital";
                document.getElementById('sub-panel').innerText = "PoLP Activo: Acceso limitado exclusivamente a registro de ventas e historial";
                modCajero.classList.remove('hidden');
                cajeroAccionesExtra.classList.remove('hidden');
                adminAccionesExtra.classList.add('hidden');
                txtBtnBuzon.innerText = "Buzón";
                
                pilaresPermitidos = ['negocio_historial'];
                keysConsultas = ['v_02_ventas_metodo_pago', 'v_06_transacciones_recientes'];

            } else {
                modCajero.classList.add('hidden');
                cajeroAccionesExtra.classList.add('hidden');
                pilaresPermitidos = ['negocio_catalogo', 'negocio_fidelidad', 'negocio_departamentos', 'negocio_historial'];

                if (rol.includes("Administrador")) {
                    adminAccionesExtra.classList.remove('hidden');
                    txtBtnBuzon.innerText = "Bandeja Sugerencias";
                } else {
                    adminAccionesExtra.classList.add('hidden');
                    txtBtnBuzon.innerText = "Buzón";
                }

                if (rol.includes("Gerente")) {
                    document.getElementById('titulo-panel').innerText = "Portal Gerencial - EcoMarket Vital";
                    document.getElementById('sub-panel').innerText = "Módulo de Control de Sucursales y Rendimiento";
                    keysConsultas = ['v_01_inventario_bajo', 'v_04_ventas_sucursal', 'v_05_empleados_sucursal', 'v_09_auditoria_crecimiento'];
                } else {
                    document.getElementById('titulo-panel').innerText = "Panel Analítico - EcoMarket Vital (Full Access)";
                    document.getElementById('sub-panel').innerText = "Esquema relacional de 6 tablas & 10 Vistas SQL avanzadas";
                    keysConsultas = [
                        'v_01_inventario_bajo', 'v_02_ventas_metodo_pago', 'v_03_facturacion_cliente',
                        'v_04_ventas_sucursal', 'v_05_empleados_sucursal', 'v_06_transacciones_recientes',
                        'v_07_ranking_empleados', 'v_08_compra_cruzada', 'v_09_auditoria_crecimiento', 'v_10_super_compradores'
                    ];
                }
            }

            pilaresPermitidos.forEach(key => {
                const c = consultasData[key];
                const btn = document.createElement('button');
                btn.onclick = () => ejecutarVista(key);
                let icono = "fa-seedling";
                if(key === 'negocio_fidelidad') icono = "fa-id-card";
                if(key === 'negocio_departamentos') icono = "fa-sitemap";
                if(key === 'negocio_historial') icono = "fa-clock-rotate-left";

                btn.className = "py-3 px-4 bg-[#1e2c21] hover:bg-[#3a5240] border border-[#4a6b52] rounded-xl text-xs font-bold text-white transition flex flex-col items-center gap-1 cursor-pointer";
                btn.innerHTML = `<i class="fa-solid ${icono} text-base text-[#a3c1ad]"></i> ${c.titulo}`;
                gridPilares.appendChild(btn);
            });

            keysConsultas.forEach(key => {
                renderizarTarjeta(key, gridConsultas);
            });
        }

        function renderizarTarjeta(key, grid) {
            const c = consultasData[key];
            let card = document.getElementById('card-' + key);
            if (!card) {
                card = document.createElement('div');
                card.id = 'card-' + key;
                card.className = "bg-[#2b3e30] border border-[#4a6b52] hover:border-[#a3c1ad] p-5 rounded-2xl flex flex-col justify-between transition-all shadow-lg group";
                grid.appendChild(card);
            }
            card.innerHTML = `
                <div>
                    <span id="badge-${key}" class="text-[10px] uppercase font-black text-[#a3c1ad] tracking-wider">${c.tipo} (${c.filas.length} registros)</span>
                    <h3 class="font-bold text-sm text-white mt-1 group-hover:text-[#a3c1ad] transition">${c.titulo}</h3>
                    <p class="text-xs text-slate-300 mt-1">${c.desc}</p>
                </div>
                <div class="mt-4">
                    <button onclick="ejecutarVista('${key}')" class="w-full py-2 bg-[#4a6b52] hover:bg-[#5c8266] text-white font-extrabold text-xs rounded-xl shadow transition cursor-pointer flex items-center justify-center gap-1.5">
                        <i class="fa-solid fa-table"></i> Ver Tabla SQL (${c.filas.length} elementos)
                    </button>
                </div>
            `;
        }

        function registrarVentaPOS() {
            const prodData = document.getElementById('pos-producto').value.split('|');
            const producto = prodData[0];
            const precio = parseFloat(prodData[1].replace('$', ''));
            const cantidad = parseInt(document.getElementById('pos-cantidad').value);
            const pago = document.getElementById('pos-pago').value;
            const total = (precio * cantidad).toFixed(2);
            
            consultasData['v_02_ventas_metodo_pago'].filas.unshift([pago, "1 (Turno Actual)", "$" + total]);

            const idVenta = "V-" + Math.floor(1000 + Math.random() * 9000);
            const fechaHora = new Date().toISOString().replace('T', ' ').substring(0, 16);
            consultasData['v_06_transacciones_recientes'].filas.unshift([idVenta, fechaHora.split(' ')[0], producto, cantidad + " un."]);
            consultasData['negocio_historial'].filas.unshift([idVenta, fechaHora, "Cliente Fidelizado", "Charallave Principal", "$" + total]);

            bitacoraLogs.unshift({
                id: "LOG-" + Math.floor(100 + Math.random() * 900),
                fecha: fechaHora,
                usuario: usuarioActualGlobal,
                accion: `Cobro POS exitoso - Factura ${idVenta} por $${total}`
            });

            if(document.getElementById('card-v_02_ventas_metodo_pago')) {
                renderizarTarjeta('v_02_ventas_metodo_pago', document.getElementById('grid-consultas'));
            }
            if(document.getElementById('card-v_06_transacciones_recientes')) {
                renderizarTarjeta('v_06_transacciones_recientes', document.getElementById('grid-consultas'));
            }

            const ticketContenido = document.getElementById('ticket-contenido');
            ticketContenido.innerHTML = `
                <p><b>Ticket:</b> ${idVenta}</p>
                <p><b>Fecha:</b> ${fechaHora}</p>
                <p><b>Producto:</b> ${producto}</p>
                <p><b>Cantidad:</b> ${cantidad} un. x $${precio.toFixed(2)}</p>
                <p><b>Método Pago:</b> ${pago}</p>
                <p class="border-t border-dashed border-[#4a6b52] pt-1 mt-1"><b>IVA Ecológico (16%):</b> $${(total * 0.16).toFixed(2)}</p>
                <p class="text-[#a3c1ad] font-bold"><b>TOTAL PAGADO: $${total}</b></p>
                <p class="text-[9px] text-[#a3c1ad] mt-2">¡Gracias por comprar ecológico! Acumulaste +${Math.floor(total * 2)} Puntos Eco.</p>
            `;
            document.getElementById('modal-ticket').classList.remove('hidden');

            const resBox = document.getElementById('pos-resultado');
            resBox.classList.remove('hidden');
            resBox.innerHTML = `
                <div class="font-bold text-[#a3c1ad] flex items-center gap-1"><i class="fa-solid fa-circle-check"></i> ¡Venta Procesada con Éxito y Persistida en Base de Datos!</div>
                <div class="text-slate-200 mt-1">Factura <b>${idVenta}</b> generada correctamente con Código QR fiscal.</div>
            `;
        }

        // Abrir Buzón adaptado según sea Administrador o Personal operativo
        function abrirBuzon() {
            const vistaEnviar = document.getElementById('buzon-vista-enviar');
            const vistaAdmin = document.getElementById('buzon-vista-admin');
            const tituloModal = document.getElementById('buzon-titulo-modal');

            if (rolActualGlobal.includes("Administrador")) {
                tituloModal.innerText = "Bandeja de Sugerencias del Personal";
                vistaEnviar.classList.add('hidden');
                vistaAdmin.classList.remove('hidden');

                const tbody = document.getElementById('tabla-buzon-admin');
                tbody.innerHTML = "";
                if(buzonMensajes.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" class="px-4 py-4 text-center text-slate-400">No hay sugerencias registradas aún.</td></tr>`;
                } else {
                    buzonMensajes.forEach(msg => {
                        tbody.innerHTML += `
                            <tr class="hover:bg-[#2b3e30]/40 transition">
                                <td class="px-4 py-3 text-[#a3c1ad] font-bold">${msg.remitente}</td>
                                <td class="px-4 py-3 text-slate-200">${msg.tipo}</td>
                                <td class="px-4 py-3 text-slate-300">${msg.mensaje}</td>
                            </tr>
                        `;
                    });
                }
            } else {
                tituloModal.innerText = "Buzón de Sugerencias y Mejoras";
                vistaAdmin.classList.add('hidden');
                vistaEnviar.classList.remove('hidden');
                document.getElementById('sug-alerta').classList.add('hidden');
                document.getElementById('sug-texto').value = '';
            }

            document.getElementById('modal-buzon').classList.remove('hidden');
        }

        function enviarSugerencia() {
            const texto = document.getElementById('sug-texto').value.trim();
            const tipo = document.getElementById('sug-tipo').value;
            if(!texto) {
                alert("Por favor, escribe el contenido de tu sugerencia.");
                return;
            }

            // Guardar en el array global para que el admin lo vea
            buzonMensajes.unshift({
                remitente: usuarioActualGlobal,
                tipo: tipo,
                mensaje: texto
            });

            const alerta = document.getElementById('sug-alerta');
            alerta.classList.remove('hidden');
            setTimeout(() => {
                document.getElementById('modal-buzon').classList.add('hidden');
            }, 1500);
        }

        function abrirBitacora() {
            const tbody = document.getElementById('tabla-bitacora-cuerpo');
            tbody.innerHTML = "";
            bitacoraLogs.forEach(log => {
                tbody.innerHTML += `
                    <tr class="hover:bg-[#2b3e30]/40 transition">
                        <td class="px-4 py-3 text-[#a3c1ad] font-mono">${log.id}</td>
                        <td class="px-4 py-3 text-slate-200">${log.fecha}</td>
                        <td class="px-4 py-3 text-slate-300">${log.usuario}</td>
                        <td class="px-4 py-3 text-slate-200">${log.accion}</td>
                    </tr>
                `;
            });
            document.getElementById('modal-bitacora').classList.remove('hidden');
        }

        function abrirArqueoCaja() {
            const historialVentas = consultasData['negocio_historial'].filas;
            const totalTransaccionesTurno = historialVentas.length;
            const modalArqueo = document.getElementById('modal-arqueo');
            const cuerpoArqueo = document.getElementById('arqueo-cuerpo');

            cuerpoArqueo.innerHTML = `
                <div class="p-3 bg-[#1e2c21] border border-[#4a6b52] rounded-xl space-y-1.5">
                    <p><b>Operador de Caja:</b> Cajero Principal (Caja 01)</p>
                    <p><b>Estado de Gaveta:</b> Cuadratura Exacta</p>
                    <p><b>Total Transacciones Registradas:</b> ${totalTransaccionesTurno} operaciones</p>
                    <p class="text-[#a3c1ad] font-bold pt-1 border-t border-[#4a6b52]">Efectivo y Divisas en Caja: (   )</p>
                </div>
                <p class="text-[11px] text-slate-300">El arqueo de turno valida las transacciones del día y genera el cierre fiscal automático para Supabase.gob.ve.</p>
            `;
            modalArqueo.classList.remove('hidden');
        }

        function cerrarSesion() {
            document.getElementById('dashboard-container').classList.add('hidden');
            document.getElementById('login-container').classList.remove('hidden');
            document.getElementById('password').value = '';
            document.getElementById('pin').value = '';
            document.getElementById('pos-resultado').classList.add('hidden');
        }

        function ejecutarVista(key) {
            const c = consultasData[key];
            let modal = document.getElementById('modal-tabla');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'modal-tabla';
                modal.className = "fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50";
                document.body.appendChild(modal);
            }

            let htmlTabla = `
                <div class="bg-[#1a241c] border border-[#4a6b52] w-full max-w-4xl rounded-3xl p-6 shadow-2xl text-white">
                    <div class="flex justify-between items-center border-b border-[#3a5240] pb-3 mb-4">
                        <div>
                            <span class="text-xs font-bold text-[#a3c1ad] uppercase tracking-widest">${c.tipo}</span>
                            <h3 class="text-lg font-bold text-white">${c.titulo}</h3>
                        </div>
                        <button onclick="document.getElementById('modal-tabla').remove()" class="text-slate-400 hover:text-white text-lg font-bold px-2.5 py-1 bg-[#2b3e30] rounded-xl">&times;</button>
                    </div>
                    <p class="text-xs text-slate-300 mb-4"><b>Descripción:</b> ${c.desc} — <i class="text-[#a3c1ad]">Mostrando ${c.filas.length} registros persistentes</i></p>
                    <div class="overflow-x-auto max-h-72 rounded-2xl border border-[#3a5240]">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-[#2b3e30] text-[#a3c1ad] uppercase font-bold">
                                <tr>
            `;
            c.columnas.forEach(col => {
                htmlTabla += `<th class="px-4 py-3">${col}</th>`;
            });
            htmlTabla += `</tr></thead><tbody class="divide-y divide-[#3a5240] bg-black/50">`;

            c.filas.forEach(fila => {
                htmlTabla += `<tr class="hover:bg-[#2b3e30]/40 transition">`;
                fila.forEach(val => {
                    htmlTabla += `<td class="px-4 py-3 text-slate-200">${val}</td>`;
                });
                htmlTabla += `</tr>`;
            });

            htmlTabla += `
                            </tbody>
                        </table>
                    </div>
                    <div class="mt-5 flex justify-end">
                        <button onclick="document.getElementById('modal-tabla').remove()" class="px-5 py-2.5 bg-[#4a6b52] hover:bg-[#5c8266] text-white text-xs font-extrabold rounded-xl cursor-pointer shadow">Cerrar Tabla</button>
                    </div>
                </div>
            `;
            modal.innerHTML = htmlTabla;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/login", methods=["POST"])
def api_login():
    datos = request.get_json()
    email = datos.get("email", "")
    password = datos.get("password", "")
    rol_seleccionado = datos.get("rol", "")
    pin = datos.get("pin", "")
    biometria = datos.get("biometria", False)

    usuario = USUARIOS_AUTORIZADOS.get(email)
    if not usuario:
        return jsonify({"mensaje": "Usuario no registrado en la base de datos de EcoMarket Vital."}), 401

    if usuario["password"] != password:
        return jsonify({"mensaje": "Contraseña incorrecta."}), 401

    if usuario["rol"] != rol_seleccionado:
        return jsonify({"mensaje": f"Acceso denegado: El usuario no posee el rol '{rol_seleccionado}'."}), 403

    if usuario["pin_2fa"] != pin:
        return jsonify({"mensaje": "Token único inválido."}), 401

    if not biometria:
        return jsonify({"mensaje": "Seguridad requerida: Debe activar la Validación Biométrica."}), 403

    BITACORA_AUDITORIA.insert(0, {
        "id": f"LOG-{len(BITACORA_AUDITORIA)+101}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": email,
        "accion": f"Login exitoso en rol: {rol_seleccionado}"
    })

    return jsonify({"status": "ok", "rol": usuario["rol"]}), 200

if __name__ == "__main__":
    app.run(debug=True)
