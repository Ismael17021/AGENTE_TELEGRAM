"""
Script para listar los grupos de Telegram y mostrar sus IDs usando la configuración MCP.
"""
import os
import json
import sys
from telethon import TelegramClient

# Leer configuración MCP
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '.vscode', 'mcp.json')
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
        tg_env = config['servers']['telegram']['env']
        API_ID = tg_env['TG_APP_ID']
        API_HASH = tg_env['TG_API_HASH']
except Exception as e:
    print(f'Error leyendo configuración MCP: {e}')
    sys.exit(1)

SESSION_NAME = 'get_group_id_session'

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print('Grupos encontrados:')
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(f'Nombre: {dialog.name} | ID: {dialog.id}')
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
