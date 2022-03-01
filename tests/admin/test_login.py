from tests.utils import ok_response


API_METHOD_LOGIN = "/admin.login"
MISSING_DATA_FIELD_MESSAGE = "Missing data for required field."

async def test_should_return_admin_data_with_valid_credentials(client, valid_admin_credentials):
    response = await client.post(
        API_METHOD_LOGIN,
        json=valid_admin_credentials,
    )

    assert response.status == 200
    response_data = await response.json()
    assert response_data == ok_response(
        data={
            "id": 1,
            "email": valid_admin_credentials["email"],
        }
    )

async def test_should_return_error_403_with_invalid_email(client, invalid_email_admin_credentials):
    response = await client.post(
        API_METHOD_LOGIN,
        json=invalid_email_admin_credentials,
    )
    assert response.status == 403
    response_data = await response.json()
    assert response_data["status"] == "forbidden"

async def test_should_return_error_403_with_invalid_password(cli, invalid_password_admin_credentials):
    response = await cli.post(
        API_METHOD_LOGIN,
        json=invalid_password_admin_credentials,
    )
    assert response.status == 403
    response_data = await response.json()
    assert response_data["status"] == "forbidden"

async def test_should_return_error_400_with_empty_credentials(cli, empty_admin_credentials):
    response = await cli.post(
        API_METHOD_LOGIN,
        json=empty_admin_credentials,
    )
    assert response.status == 400
    response_data = await response.json()
    assert response_data["status"] == "bad_request"
    assert response_data["data"] == {
        "email": [MISSING_DATA_FIELD_MESSAGE],
        "password": [MISSING_DATA_FIELD_MESSAGE]
    }