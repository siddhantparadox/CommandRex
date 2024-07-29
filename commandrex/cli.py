import click
import subprocess
from .nlp import process_command
import logging

logger = logging.getLogger(__name__)

@click.command()
@click.argument('command', nargs=-1)
def cli(command):
    """CommandRex: Your natural language command-line interface."""
    user_input = ' '.join(command)
    if not user_input:
        click.echo("Please provide a command.")
        return

    click.echo(f"Processing command: {user_input}")
    windows_command = process_command(user_input)

    if windows_command:
        click.echo(f"Translated command: {windows_command}")
        click.echo("Executing command...")
        try:
            result = subprocess.run(windows_command, shell=True, text=True, capture_output=True)
            click.echo(result.stdout)
            if result.stderr:
                click.echo(f"Errors: {result.stderr}", err=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Error executing command: {e}", err=True)
    else:
        click.echo("Failed to process the command. Please check the logs for more information and try again.")

if __name__ == '__main__':
    cli()