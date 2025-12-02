from unittest.mock import patch

import pytest
from src.services.registration_services import (
    StartRegistrationService,
    VerifyCodeService,
)
from src.exceptions.registration_exceptions import (
    UsernameAlreadyUsedException,
    UserIsAlreadyActiveException,
    InvalidVerificationCodeException,
    ServerNotDetectTGException,
)
from .conftest import FakeUser, FakeVerificationCode


# ---------------------- StartRegistrationService ----------------------
@pytest.mark.asyncio
async def test_start_registration_success(
        mock_session, mock_get_user_by_name_service, mock_create_user_service
):
    mock_get_user_by_name_service.exec.return_value = None
    mock_create_user_service.exec.return_value = FakeUser(id=1)

    service = StartRegistrationService(
        session=mock_session,
        get_user_by_name_service=mock_get_user_by_name_service,
        create_user_service=mock_create_user_service
    )

    with patch("src.services.registration_services.encode_record_id", return_value="encoded_id"):
        verification_code = await service.exec(username="newuser", password="pass")

    assert verification_code.encode_id == "encoded_id"


@pytest.mark.asyncio
async def test_start_registration_username_taken(
    mock_session, mock_get_user_by_name_service, mock_create_user_service
):
    mock_get_user_by_name_service.exec.return_value = FakeUser()
    service = StartRegistrationService(
        session=mock_session,
        get_user_by_name_service=mock_get_user_by_name_service,
        create_user_service=mock_create_user_service,
    )

    with pytest.raises(UsernameAlreadyUsedException):
        await service.exec(username="existinguser", password="pass")


# ---------------------- VerifyCodeService ----------------------
@pytest.mark.asyncio
async def test_verify_code_success(
    mock_session, mock_get_user_service, mock_get_verification_code_service
):
    user = FakeUser(id=1)
    code = 123456
    verification = FakeVerificationCode(id=1, user_id=1, code=code)

    mock_get_user_service.exec.return_value = user
    mock_get_verification_code_service.exec.return_value = verification

    service = VerifyCodeService(
        session=mock_session,
        get_verification_code_service=mock_get_verification_code_service,
        get_not_active_user_serivce=mock_get_user_service
    )

    tokens = await service.exec(user_id=1, code=code)
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
    assert user.is_active is True
    assert verification.activate is True


@pytest.mark.asyncio
async def test_verify_code_user_already_active(
    mock_session, mock_get_user_service, mock_get_verification_code_service
):
    user = FakeUser(is_active=True)
    verification = FakeVerificationCode()

    mock_get_user_service.exec.return_value = user
    mock_get_verification_code_service.exec.return_value = verification

    service = VerifyCodeService(
        session=mock_session,
        get_verification_code_service=mock_get_verification_code_service,
        get_not_active_user_serivce=mock_get_user_service
    )

    with pytest.raises(UserIsAlreadyActiveException):
        await service.exec(user_id=1, code=123456)


@pytest.mark.asyncio
async def test_verify_code_invalid_code(
    mock_session, mock_get_user_service, mock_get_verification_code_service
):
    user = FakeUser()
    verification = FakeVerificationCode(code=111111)

    mock_get_user_service.exec.return_value = user
    mock_get_verification_code_service.exec.return_value = verification

    service = VerifyCodeService(
        session=mock_session,
        get_verification_code_service=mock_get_verification_code_service,
        get_not_active_user_serivce=mock_get_user_service
    )

    with pytest.raises(InvalidVerificationCodeException):
        await service.exec(user_id=1, code=123456)


@pytest.mark.asyncio
async def test_verify_code_no_tg_id(
    mock_session, mock_get_user_service, mock_get_verification_code_service
):
    user = FakeUser()
    verification = FakeVerificationCode(tg_user_id=None)

    mock_get_user_service.exec.return_value = user
    mock_get_verification_code_service.exec.return_value = verification

    service = VerifyCodeService(
        session=mock_session,
        get_verification_code_service=mock_get_verification_code_service,
        get_not_active_user_serivce=mock_get_user_service
    )

    with pytest.raises(ServerNotDetectTGException):
        await service.exec(user_id=1, code=verification.code)
