from tests.utils import ok_response


API_METHOD_LOGIN = "/admin.current"

async def test_should_return_data_for_authorized_admin(cli, authenticated_admin, valid_admin_credentials):
    response = await cli.get(API_METHOD_LOGIN)

    assert response.status == 200
    response_data = await response.json()
    assert response_data["status"] == "ok"
    assert response_data["data"]["email"] == valid_admin_credentials["email"]

async def test_should_return_error_401_for_unauthorized_admin(cli):
    response = await cli.get(API_METHOD_LOGIN)
    assert response.status == 401