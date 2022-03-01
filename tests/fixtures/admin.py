from pytest import fixture


@fixture(autouse=True)
def accessor(app):
    app.on_startup.append(app.storage.admins.connect)
    app.on_shutdown.append(app.storage.admins.disconnect)

@fixture
def valid_admin_credentials(app):
    return {
        "email": app.config.admin.email,
        "password": app.config.admin.password,
    }

@fixture
def invalid_email_admin_credentials(app):
    return {
        "email": f"wrong.{app.config.admin.email}",
        "password": app.config.admin.password,
    }

@fixture
def invalid_password_admin_credentials(app):
    return {
        "email": app.config.admin.email,
        "password": app.config.admin.password[1:],
    }

@fixture
def empty_admin_credentials(app):
    return {}

@fixture
async def authenticated_admin(cli, valid_admin_credentials):
    await cli.post(
        "/admin.login",
        data=valid_admin_credentials,
    )
