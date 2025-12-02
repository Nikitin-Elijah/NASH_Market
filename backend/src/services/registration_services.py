from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import hash_password, create_access_token, create_refresh_token
from src.config import VERIFICATION_SECRET_KEY
from src.database.db_depends import get_async_db
from src.exceptions.registration_exceptions import (
    UsernameAlreadyUsedException,
    VerificationCodeNotFoundException,
    UserIsAlreadyActiveException,
    VerificationCodeUsedException,
    InvalidVerificationCodeException,
    ServerNotDetectTGException,
)
from src.exceptions.user_exceptions import UserNotFoundException
from src.models import UserModel, VerificationCode
from src.services.user_services import GetUserByNameService, GetNotActiveUserService
from src.utils import generate_six_digit_code, encode_record_id


class CreateUserService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _create_user(self, username: str, password: str) -> UserModel:
        user = UserModel(username=username, hashed_password=hash_password(password))
        self.session.add(user)
        await self.session.commit()
        return user

    async def exec(self, username: str, password: str) -> UserModel:
        return await self._create_user(username=username, password=password)


class GetVerificationCodeService:
    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        self.session = session

    async def _get_verification_code(self, user_id: int) -> VerificationCode | None:
        verification_code = await self.session.scalar(
            select(VerificationCode).where(VerificationCode.user_id == user_id)
        )
        return verification_code

    @staticmethod
    def _validate(verification_code: VerificationCode | None):
        if not verification_code:
            raise VerificationCodeNotFoundException("Verification code not found")

    async def exec(self, user_id: int) -> VerificationCode:
        verification_code = await self._get_verification_code(user_id=user_id)
        self._validate(verification_code=verification_code)
        return verification_code


class StartRegistrationService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_user_by_name_service: GetUserByNameService = Depends(),
        create_user_service: CreateUserService = Depends(),
    ):
        self.session = session
        self.get_user_by_name_service = get_user_by_name_service
        self.create_user_service = create_user_service

    async def _create_code(self, user: UserModel) -> VerificationCode:
        verification_code = VerificationCode(
            user_id=user.id,
            code=generate_six_digit_code(),
            encode_id=encode_record_id(
                record_id=user.id, secret_key=VERIFICATION_SECRET_KEY.encode()
            ),
        )
        self.session.add(verification_code)
        await self.session.commit()
        return verification_code

    @staticmethod
    def _validate(user: UserModel):
        if user:
            raise UsernameAlreadyUsedException("Username is already used")

    async def exec(self, username: str, password: str) -> VerificationCode:
        user = await self.get_user_by_name_service.exec(username=username)
        self._validate(user=user)
        user = await self.create_user_service.exec(username=username, password=password)
        verification_code = await self._create_code(user=user)
        return verification_code


class VerifyCodeService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_verification_code_service: GetVerificationCodeService = Depends(),
        get_not_active_user_serivce: GetNotActiveUserService = Depends()
    ):
        self.session = session
        self.get_verification_code_service = get_verification_code_service
        self.get_not_active_user_service = get_not_active_user_serivce

    async def _verify_code(
        self, user: UserModel, verification_code: VerificationCode
    ) -> dict:
        verification_code.activate = True
        user.tg_user_id = verification_code.tg_user_id
        user.tg_username = verification_code.tg_username
        user.is_active = True
        user.verified_at = datetime.now()
        await self.session.commit()
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def _validate(user: UserModel, verification_code: VerificationCode, code: int):
        if user.is_active:
            raise UserIsAlreadyActiveException("User is already active")
        if verification_code.activate:
            raise VerificationCodeUsedException("Verification code is already used")
        if str(verification_code.code).strip() != str(code).strip():
            raise InvalidVerificationCodeException("Invalid verification code")
        if not verification_code.tg_user_id:
            raise ServerNotDetectTGException("The server did not detect tg id")

    async def exec(self, user_id: int, code: int) -> dict:
        user = await self.get_not_active_user_service.exec(user_id=user_id)
        verification_code = await self.get_verification_code_service.exec(
            user_id=user_id
        )
        self._validate(user=user, verification_code=verification_code, code=code)
        return await self._verify_code(user=user, verification_code=verification_code)


class UpdateVerificationCodeService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_db),
        get_verification_code: GetVerificationCodeService = Depends(),
    ):
        self.session = session
        self.get_verification_code = get_verification_code

    async def _update_verification_code(
        self, verification_code: VerificationCode, tg_user_id: int, tg_username: str
    ) -> VerificationCode:
        verification_code.tg_user_id = tg_user_id
        verification_code.tg_username = tg_username
        await self.session.commit()
        return verification_code

    async def exec(
        self, user_id: int, tg_user_id: int, tg_username: str
    ) -> VerificationCode:
        verification_code = await self.get_verification_code.exec(user_id=user_id)
        return await self._update_verification_code(
            verification_code=verification_code,
            tg_user_id=tg_user_id,
            tg_username=tg_username,
        )
