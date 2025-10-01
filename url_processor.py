"""
Módulo para procesar URLs: obtener contenido, resumir y extraer imagen principal.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Extrae el texto principal de una página web
def extract_main_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Busca el título
        title = soup.title.string if soup.title else ''
        # Busca el primer párrafo largo
        paragraphs = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 80]
        main_text = paragraphs[0] if paragraphs else ''
        return title, main_text
    except Exception as e:
        return '', f'Error al procesar la URL: {e}'

# Extrae la imagen principal (og:image o primera imagen)
def extract_main_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Busca og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        # Busca la primera imagen
        img = soup.find('img')
        if img and img.get('src'):
            img_url = img['src']
            # Si la URL es relativa, la convierte en absoluta
            if not urlparse(img_url).netloc:
                img_url = urlparse(url)._replace(path=img_url).geturl()
            return img_url
        return ''
    except Exception:
        return ''

# Genera un resumen simple (puedes mejorar con IA)
def summarize_text(text, max_length=200):
    return text[:max_length] + ('...' if len(text) > max_length else '')

# Procesa una URL y devuelve un resumen estructurado
def process_url(url):
    title, main_text = extract_main_text(url)
    image_url = extract_main_image(url)
    summary = summarize_text(main_text)
    return {
        'title': title,
        'summary': summary,
        'url': url,
        'image': image_url
    }
