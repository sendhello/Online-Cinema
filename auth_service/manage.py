#!/usr/bin/python
import asyncio
import getpass
import subprocess

import typer
from fastapi import HTTPException
from models import Role, Rules, User
from sqlalchemy.exc import IntegrityError
from starlette import status


async def create_user(login: str, password: str) -> User:
    try:
        user = await User.create(
            login=login,
            password=password,
            first_name='',
            last_name='',
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with such login is registered already',
        )

    try:
        role = await Role.create(title='super_admin')

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Role with such title already exists',
        )

    rule = Rules.admin_rules
    role.rules = [rule.value]
    await role.save()

    user.role = role
    await user.save()

    return user


app = typer.Typer()


@app.command()
def makemigrations(text: str):
    """Create migration with text."""
    result = subprocess.run(
        ['alembic', 'revision', '--autogenerate', '-m', f'"{text}"'],
        capture_output=True,
        text=True,
    )
    print('Log:', result.stdout)
    print('Errors:', result.stderr)


@app.command()
def migrate():
    """Upgrade migration."""
    result = subprocess.run(
        ['alembic', 'upgrade', 'head'], capture_output=True, text=True
    )
    print('Log:', result.stdout)
    print('Errors:', result.stderr)


@app.command()
def rollback(migrate_hash: str):
    """Downgrade migration."""
    result = subprocess.run(
        ['alembic', 'downgrade', migrate_hash], capture_output=True, text=True
    )
    print('Log:', result.stdout)
    print('Errors:', result.stderr)


@app.command()
def createsuperuser(login: str = 'admin', password: str = 'admin'):
    """Creating super admin."""
    loop = asyncio.get_event_loop()
    super_admin = loop.run_until_complete(create_user(login, password))

    print(f'Super user "{super_admin.login}" created')


if __name__ == "__main__":
    app()
