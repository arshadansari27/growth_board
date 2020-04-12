"""
    Client Application for Data Import System
"""
import click


@click.command()
@click.pass_context
def cli(ctx):
    """
        Click client caller command group
    """
    ctx.obj = {}
    print("Running on command line...")
