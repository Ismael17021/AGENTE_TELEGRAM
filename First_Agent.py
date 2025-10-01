# Archivo renombrado: First_Agent.py
# ...existing code from main.py will be placed here...

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from telegram_mcp_agent import run_telegram_agent
from infojobs_api import run_infojobs_tools

def esperar_salir():
    from rich.prompt import Prompt
    while True:
        comando = Prompt.ask("[bold yellow]Escribe 'sal' para volver al menú principal[/bold yellow]")
        if comando.strip().lower() == 'sal':
            break

def main():
    console = Console()
    while True:
        console.clear()
        console.rule("[bold blue]Agente Principal[/bold blue]")
        table = Table(title="Selecciona una herramienta", show_header=True, header_style="bold magenta")
        table.add_column("Opción", style="dim", width=12)
        table.add_column("Herramienta")
        table.add_row("1", "Agente Telegram (monitoriza, resume y exporta)")
        table.add_row("2", "Herramientas Infojobs (próximamente)")
        table.add_row("0", "Salir")
        console.print(table)
        choice = Prompt.ask("[bold green]Introduce el número de la opción[/bold green]", choices=["1", "2", "0"])
        if choice == "1":
            run_telegram_agent()
            esperar_salir()
        elif choice == "2":
            run_infojobs_tools()
            esperar_salir()
        elif choice == "0":
            console.print("[bold red]Saliendo...[/bold red]")
            break

if __name__ == "__main__":
    main()
