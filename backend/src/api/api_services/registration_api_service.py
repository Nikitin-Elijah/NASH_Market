from fastapi import Depends, HTTPException, status

from src.exceptions.registration_exceptions import (
    UsernameAlreadyUsedException,
    VerificationCodeNotFoundException,
    UserIsAlreadyActiveException,
    VerificationCodeUsedException,
    InvalidVerificationCodeException,
    ServerNotDetectTGException,
)
from src.exceptions.user_exceptions import UserNotFoundException
from src.models import VerificationCode
from src.services.registration_services import (
    StartRegistrationService,
    VerifyCodeService,
    GetVerificationCodeService,
    UpdateVerificationCodeService,
)


class GetVerificationCodeAPIService:
    """
    API Сервис для получения кода верификации по id нового пользователя
    """

    def __init__(
        self,
        get_verification_code_service: GetVerificationCodeService = Depends(

        ),
    ):
        self.get_verification_code_service = get_verification_code_service

    async def exec(self, user_id: int) -> VerificationCode:
        try:
            return await self.get_verification_code_service.exec(user_id=user_id)
        except VerificationCodeNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class StartRegistrationAPIService:
    """
    API Сервис для старта регистрации
    """

    def __init__(
        self,
        start_registration_service: StartRegistrationService = Depends(

        ),
    ):
        self.start_registration_service = start_registration_service

    async def exec(self, username: str, password: str) -> VerificationCode:
        try:
            return await self.start_registration_service.exec(
                username=username, password=password
            )
        except UsernameAlreadyUsedException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class VerifyCodeAPIService:
    """
    API Сервис для проверки кода подтверждения
    """

    def __init__(
        self, verify_code_service: VerifyCodeService = Depends()
    ):
        self.verify_code_service = verify_code_service

    async def exec(self, user_id: int, code: int) -> dict:
        try:
            return await self.verify_code_service.exec(user_id=user_id, code=code)
        except UserNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except VerificationCodeNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserIsAlreadyActiveException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except VerificationCodeUsedException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except InvalidVerificationCodeException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except ServerNotDetectTGException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdateVerificationCodeAPIService:
    """
    API Сервис для сохранения telegram id и username
    """

    def __init__(
        self,
        update_verification_code_api_service: UpdateVerificationCodeService = Depends(),
    ):
        self.update_verification_code_api_service = update_verification_code_api_service

    async def exec(
        self, user_id: int, tg_user_id: int, tg_username: str
    ) -> VerificationCode:
        return await self.update_verification_code_api_service.exec(
            user_id=user_id, tg_user_id=tg_user_id, tg_username=tg_username
        )
