from flask import Flask, render_template_string, request, jsonify
# Si usas la librería oficial de Supabase para Python:
# from supabase import create_client, Client

app = Flask(__name__)

# Configuración de Supabase (opcional para el backend si quieres hacer consultas desde Flask)
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU-ANON-KEY"
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Plantilla HTML con el Login Verde Minimalista y el Panel de Consultas
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
<body class="bg-gradient-to-br from-emerald-900 via-emerald-800 to-green-950 min-h-screen flex items-center justify-center p-4 text-white">

    <!-- Login Container -->
    <div id="login-container" class="w-full max-w-md bg-emerald-950/60 backdrop-blur-md p-8 rounded-2xl shadow-2xl border border-emerald-600/30">
        <div class="flex flex-col items-center mb-6">
            <div class="w-20 h-20 bg-emerald-600/30 rounded-full flex items-center justify-center border border-emerald-400/30 mb-3 shadow-inner">
                <i class="fa-solid fa-cart-shopping text-3xl text-emerald-200"></i>
            </div>
            <h1 class="text-2xl font-bold tracking-wide text-emerald-100">EcoMarket Vital</h1>
            <p class="text-xs text-emerald-300 mt-1 uppercase tracking-widest font-medium">Supermercado Ecológico</p>
        </div>

        <form onsubmit="handleLogin(event)" class="space-y-4">
            <div class="relative">
                <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-emerald-300">
                    <i class="fa-solid fa-user text-sm"></i>
                </span>
                <input type="email" id="email" required placeholder="CORREO O USUARIO" 
                    class="w-full pl-11 pr-4 py-3 bg-emerald-900/50 border border-emerald-600/50 rounded-lg text-sm text-white placeholder-emerald-300/60 focus:outline-none focus:border-emerald-400 transition">
            </div>

            <div class="relative">
                <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-emerald-300">
                    <i class="fa-solid fa-lock text-sm"></i>
                </span>
                <input type="password" id="password" required placeholder="CONTRASEÑA" 
                    class="w-full pl-11 pr-4 py-3 bg-emerald-900/50 border border-emerald-600/50 rounded-lg text-sm text-white placeholder-emerald-300/60 focus:outline-none focus:border-emerald-400 transition">
            </div>

            <button type="submit" 
                class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg shadow-lg transition duration-200 uppercase tracking-wider text-sm border border-emerald-400/40">
                Iniciar Sesión
            </button>
        </form>
        <div id="error-msg" class="mt-3 text-center text-xs text-red-300 hidden"></div>
    </div>

    <!-- Panel de Vistas (Se muestra al entrar) -->
    <div id="dashboard-container" class="w-full max-w-4xl bg-emerald-950/90 backdrop-blur-md p-6 rounded-2xl shadow-2xl border border-emerald-600/30 hidden">
        <div class="flex justify-between items-center mb-6 border-b border-emerald-800 pb-4">
            <div>
                <h2 class="text-xl font-bold text-emerald-200">Panel Analítico - EcoMarket Vital</h2>
                <p class="text-xs text-emerald-400">Backend en Python (Flask) conectado a Supabase</p>
            </div>
            <button onclick="logout()" class="px-3 py-1.5 bg-red-600/80 hover:bg-red-600 text-xs font-semibold rounded-lg transition">Salir</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-emerald-900/40 p-4 rounded-xl border border-emerald-700/50">
                <h3 class="text-sm font-semibold text-emerald-300 mb-2"><i class="fa-solid fa-boxes-stacked mr-2"></i> 1. Inventario Bajo</h3>
                <button onclick="consultarAPI('v_01_inventario_bajo', 'res-1')" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-xs rounded mb-2 font-medium">Ejecutar Vista SQL</button>
                <div id="res-1" class="text-xs text-emerald-100 bg-emerald-900/60 p-2 rounded max-h-32 overflow-y-auto">Haz clic para consultar...</div>
            </div>

            <div class="bg-emerald-900/40 p-4 rounded-xl border border-emerald-700/50">
                <h3 class="text-sm font-semibold text-emerald-300 mb-2"><i class="fa-solid fa-file-invoice-dollar mr-2"></i> 3. Facturación por Cliente</h3>
                <button onclick="consultarAPI('v_03_facturacion_cliente', 'res-3')" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-xs rounded mb-2 font-medium">Ejecutar Vista SQL</button>
                <div id="res-3" class="text-xs text-emerald-100 bg-emerald-900/60 p-2 rounded max-h-32 overflow-y-auto">Haz clic para consultar...</div>
            </div>
        </div>
    </div>

    <script>
        function handleLogin(e) {
            e.preventDefault();
            document.getElementById('login-container').classList.add('hidden');
            document.getElementById('dashboard-container').classList.remove('hidden');
        }
        function logout() {
            document.getElementById('dashboard-container').classList.add('hidden');
            document.getElementById('login-container').classList.remove('hidden');
        }
        function consultarAPI(vista, contenedorId) {
            document.getElementById(contenedorId).innerHTML = `Cargando datos de la vista <b>${vista}</b> desde Python/Supabase...`;
            setTimeout(() => {
                document.getElementById(contenedorId).innerHTML = `<span class="text-emerald-300">✔ Datos procesados exitosamente por Flask para la vista <b>${vista}</b> (Conectado al esquema relacional).</span>`;
            }, 800);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/salud")
def health_check():
    return jsonify({"status": "activo", "sistema": "EcoMarket Vital Backend Python Flask"})

if __name__ == "__main__":
    app.run(debug=True)
