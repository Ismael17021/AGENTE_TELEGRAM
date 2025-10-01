# Función principal para menú

import time
from telethon.sync import TelegramClient

def buscar_ofertas_ingeniero():
    """
    Busca ofertas de Infojobs para ingenieros (eléctrico, electrónico, etc.) con <=1 año de experiencia o sin experiencia.
    """
    # Parámetros de búsqueda
    keywords = [
        "ingeniero", "ingeniera", "ingeniero eléctrico", "ingeniero electronico", "ingeniero industrial",
        "ingeniero automatización", "ingeniero junior", "ingeniero sin experiencia", "ingeniero telecomunicaciones"
    ]
    experiencia = [0, 1]  # 0: sin experiencia, 1: 1 año
    params = {
        "q": " ".join(keywords),
        "category": "ingenieria-tecnica,ingenieria-superior,ingenieria-tecnica-industrial,ingenieria-industrial",
        "experienceMin": 0,
        "maxResults": 10
    }
    ofertas = []
    try:
        # Endpoint oficial de Infojobs para ofertas
        url = "https://api.infojobs.net/api/9/offer"
        access_token = get_access_token()
        if not access_token:
            print("No access_token disponible para Infojobs.")
            return []
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for oferta in data.get("offers", []):
                # Filtrar por experiencia
                exp = oferta.get("experienceMin", 0)
                if exp in experiencia:
                    ofertas.append(oferta)
        else:
            print(f"Error Infojobs: {response.status_code}")
    except Exception as e:
        print(f"Error buscando ofertas: {e}")
    return ofertas

def enviar_ofertas_telegram(ofertas, group_id, api_id, api_hash, session_name="telegram_agent_session"):
    """Envía las ofertas encontradas al grupo de Telegram indicado."""
    with TelegramClient(session_name, api_id, api_hash) as client:
        for oferta in ofertas:
            titulo = oferta.get("title", "Sin título")
            empresa = oferta.get("author", {}).get("name", "")
            url = oferta.get("link", "")
            salario = oferta.get("salaryDescription", "")
            ubicacion = oferta.get("province", {}).get("value", "")
            experiencia = oferta.get("experienceMin", "")
            mensaje = f"🛠️ Nueva oferta Infojobs\n\n" \
                      f"🔹 Puesto: {titulo}\n" \
                      f"🏢 Empresa: {empresa}\n" \
                      f"📍 Ubicación: {ubicacion}\n" \
                      f"💼 Experiencia mínima: {experiencia}\n" \
                      f"💰 Salario: {salario}\n" \
                      f"🔗 Más info: {url}"
            client.send_message(group_id, mensaje)

def run_infojobs_tools():
    print("[Infojobs] Buscando ofertas de empleo de ingeniero (sin experiencia o 1 año) y notificando en Telegram...")
    # Leer credenciales de Telegram
    config_path = os.path.join(os.path.dirname(__file__), '.vscode', 'mcp.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            tg_env = config['servers']['telegram']['env']
            api_id = tg_env['TG_APP_ID']
            api_hash = tg_env['TG_API_HASH']
    except Exception as e:
        print(f'Error leyendo configuración MCP: {e}')
        return
    # ID del grupo de Prueba (ajusta aquí el ID de tu grupo de pruebas)
    GROUP_PRUEBA = -1001234567890  # <-- Cambia por el ID real de tu grupo de pruebas
    ofertas_previas = set()
    import threading
    stop_event = threading.Event()

    def input_listener():
        while not stop_event.is_set():
            try:
                comando = input("[Escribe 'sal' para volver al menú principal]: ").strip().lower()
                if comando == 'sal':
                    confirm = input("¿Seguro que quieres salir de Infojobs? (si/no): ").strip().lower()
                    if confirm in ('si', 's'):
                        stop_event.set()
                        print("\n[Saliendo de Infojobs...]")
                        break
                    else:
                        print("Continuando con Infojobs.")
            except EOFError:
                break

    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

    while not stop_event.is_set():
        ofertas = buscar_ofertas_ingeniero()
        nuevas = []
        for oferta in ofertas:
            if oferta['id'] not in ofertas_previas:
                nuevas.append(oferta)
                ofertas_previas.add(oferta['id'])
        if nuevas:
            enviar_ofertas_telegram(nuevas, GROUP_PRUEBA, api_id, api_hash)
            print(f"{len(nuevas)} nuevas ofertas enviadas a Telegram.")
        else:
            print("Sin novedades de ofertas.")
        for _ in range(30):
            if stop_event.is_set():
                break
            time.sleep(10)  # Espera total 5 minutos, comprobando stop_event
"""
Módulo base para futura integración con la API de Infojobs usando OAuth2.
Incluye estructura para guardar tokens y realizar peticiones autenticadas.
"""

import os
import json
import requests

# Leer credenciales Infojobs desde .vscode/mcp.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '.vscode', 'mcp.json')
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
        ij_env = config['servers']['infojobs']['env']
        INFOJOBS_CLIENT_ID = ij_env['INFOJOBS_CLIENT_ID']
        INFOJOBS_CLIENT_SECRET = ij_env['INFOJOBS_CLIENT_SECRET']
        INFOJOBS_REDIRECT_URI = ij_env.get('INFOJOBS_REDIRECT_URI', 'http://localhost:8080/callback')
except Exception as e:
    print(f'Error leyendo configuración Infojobs: {e}')
    INFOJOBS_CLIENT_ID = ''
    INFOJOBS_CLIENT_SECRET = ''
    INFOJOBS_REDIRECT_URI = 'http://localhost:8080/callback'
TOKEN_FILE = 'infojobs_token.json'

# Guardar y cargar token

def save_token(token_data):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(token_data, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# Flujo OAuth2 completo para Infojobs
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

def get_access_token():
    token_data = load_token()
    if token_data and 'access_token' in token_data:
        return token_data['access_token']
    print('No hay access_token disponible. Iniciando flujo OAuth2...')
    # Paso 1: Solicitar autorización al usuario
    auth_url = (
        "https://www.infojobs.net/api/oauth/user-authorize/index.xhtml?" +
        urlencode({
            "client_id": INFOJOBS_CLIENT_ID,
            "redirect_uri": INFOJOBS_REDIRECT_URI,
            "response_type": "code",
            "scope": "curriculum-read cv job-offers-read"
        })
    )
    print("Abre el siguiente enlace en tu navegador y autoriza la aplicación:")
    print(auth_url)
    webbrowser.open(auth_url)

    # Paso 2: Esperar el código de autorización en el redirect_uri
    code = None
    class OAuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal code
            query = urlparse(self.path).query
            params = parse_qs(query)
            if 'code' in params:
                code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Autorizacion completada. Puedes cerrar esta ventana.</h1>')
            else:
                self.send_response(400)
                self.end_headers()

    # Iniciar servidor temporal para capturar el código
    url_parts = urlparse(INFOJOBS_REDIRECT_URI)
    server_address = (url_parts.hostname, url_parts.port)
    httpd = HTTPServer(server_address, OAuthHandler)
    print(f"Esperando autorización en {INFOJOBS_REDIRECT_URI} ...")
    while code is None:
        httpd.handle_request()
    httpd.server_close()

    # Paso 3: Intercambiar el código por un access_token
    token_url = "https://www.infojobs.net/oauth/authorize"
    data = {
        "grant_type": "authorization_code",
        "client_id": INFOJOBS_CLIENT_ID,
        "client_secret": INFOJOBS_CLIENT_SECRET,
        "code": code,
        "redirect_uri": INFOJOBS_REDIRECT_URI
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        save_token(token_data)
        print("Token de acceso guardado correctamente.")
        return token_data['access_token']
    else:
        print(f"Error al obtener el token: {response.status_code} {response.text}")
        return None

# Función para hacer peticiones autenticadas a la API de Infojobs
def infojobs_api_get(endpoint):
    access_token = get_access_token()
    if not access_token:
        print('No se puede hacer la petición: falta access_token.')
        return None
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.infojobs.net/api/1/{endpoint}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print(f"Error en la petición a Infojobs: {response.status_code}")
    return None

# Ejemplo de uso futuro:
if __name__ == "__main__":
    # Cuando tengas el token, puedes probar:
    perfil = infojobs_api_get('curriculum')
    print('Perfil Infojobs:', perfil)
