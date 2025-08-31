#!/usr/bin/env python3
"""
Database management CLI script
"""

import asyncio
import click
import logging
from pathlib import Path
import sys

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.init_db import init_database, reset_database
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Database management commands for English Learning Platform"""
    pass


@cli.command()
def init():
    """Initialize the database with tables and initial data"""
    click.echo("Initializing database...")
    try:
        asyncio.run(init_database())
        click.echo("✅ Database initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Database initialization failed: {e}")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to reset the database? This will delete all data!")
def reset():
    """Reset the database (development only)"""
    if settings.ENVIRONMENT != "development":
        click.echo("❌ Database reset is only allowed in development environment")
        sys.exit(1)
    
    click.echo("Resetting database...")
    try:
        asyncio.run(reset_database())
        click.echo("✅ Database reset successfully!")
    except Exception as e:
        click.echo(f"❌ Database reset failed: {e}")
        sys.exit(1)


@cli.command()
def check():
    """Check database connection and health"""
    click.echo("Checking database connection...")
    try:
        from app.core.database import check_db_health
        is_healthy = asyncio.run(check_db_health())
        
        if is_healthy:
            click.echo("✅ Database connection is healthy")
        else:
            click.echo("❌ Database connection failed")
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Database check failed: {e}")
        sys.exit(1)


@cli.command()
def info():
    """Show database configuration information"""
    click.echo("Database Configuration:")
    click.echo(f"  Environment: {settings.ENVIRONMENT}")
    click.echo(f"  Database URL: {settings.DATABASE_URL}")
    click.echo(f"  Pool Size: {settings.DATABASE_POOL_SIZE}")
    click.echo(f"  Max Overflow: {settings.DATABASE_MAX_OVERFLOW}")


if __name__ == "__main__":
    cli()