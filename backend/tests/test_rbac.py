import pytest
from fastapi import HTTPException

from app.api.deps import _user_role, require_roles


@pytest.mark.parametrize(
    ("user", "expected"),
    [
        ({"payload": {"role": "ward_officer"}}, "WARD_OFFICER"),
        ({"payload": {"public_metadata": {"role": " admin "}}}, "ADMIN"),
        ({"payload": {"metadata": {"role": "citizen"}}}, "CITIZEN"),
        ({"payload": {"public_metadata": "invalid"}}, None),
        ({"payload": None}, None),
    ],
)
def test_user_role_normalizes_supported_claims(user, expected):
    assert _user_role(user) == expected


def test_require_roles_allows_authorized_user_and_rejects_citizen():
    dependency = require_roles(["WARD_OFFICER", "ADMIN"])
    officer = {"payload": {"public_metadata": {"role": "ward_officer"}}}
    citizen = {"payload": {"role": "CITIZEN"}}
    assert dependency(officer) is officer
    with pytest.raises(HTTPException) as error:
        dependency(citizen)
    assert error.value.status_code == 403
    assert error.value.detail == "Permission denied"


def test_single_role_string_is_not_split_into_characters():
    dependency = require_roles("ADMIN")
    admin = {"payload": {"role": "ADMIN"}}
    assert dependency(admin) is admin
