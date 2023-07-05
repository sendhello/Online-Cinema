#!/usr/bin/python
import asyncio
import getpass

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


def get_credentials() -> tuple[str, str] | None:
    login = input('Username (admin): ')
    if not login:
        login = 'admin'

    password = getpass.getpass('Password (admin): ')
    if not password:
        password = 'admin'

    re_password = getpass.getpass('Repeat password: ')
    if not re_password:
        re_password = 'admin'

    if password != re_password:
        print('Passwords not match')
        return None

    return login, password


app = typer.Typer()


@app.command()
def help():
    print('RUN: python manage.py createsuperuser')


@app.command()
def createsuperuser():
    login, password = get_credentials()
    loop = asyncio.get_event_loop()
    super_admin = loop.run_until_complete(create_user(login, password))

    print(f'Super user "{super_admin.login}" created')


if __name__ == "__main__":
    app()
