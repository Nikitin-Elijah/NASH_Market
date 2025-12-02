from fastapi import APIRouter, Depends
from fastapi.params import Query

from src.api.api_services.registration_api_service import (
    StartRegistrationAPIService,
    VerifyCodeAPIService,
    GetVerificationCodeAPIService,
    UpdateVerificationCodeAPIService,
)
from src.api.schemas.users import UserCreate
from src.api.schemas.verification_code import (
    VerificationCodeSchema,
    VerifyCodeSchema,
    ProtectVerificationCodeSchema,
)
from src.dependencies.api_key import validate_api_key
from src.utils import generate_invite_link

router = APIRouter(prefix="/reg", tags=["registration"])


@router.get(
    "/{user_id}",
    response_model=ProtectVerificationCodeSchema,
    dependencies=[Depends(validate_api_key)],
)
async def get_verification_code(
    user_id: int,
    get_verification_code_api_service: GetVerificationCodeAPIService = Depends(),
):
    result = await get_verification_code_api_service.exec(user_id=user_id)
    print(result.__dict__)
    return result


@router.post("/register/", response_model=VerificationCodeSchema)
async def create_user(
    user: UserCreate,
    start_registration_api_service: StartRegistrationAPIService = Depends(),
):
    verification_code = await start_registration_api_service.exec(
        username=user.username, password=user.password
    )
    print("-" * 100, verification_code.__dict__)
    return VerificationCodeSchema(
        id=verification_code.id,
        user_id=verification_code.user_id,
        tg_url=generate_invite_link(reg_hash=verification_code.encode_id),
    )


@router.post("/verify-code/")
async def verify_code(
    verify_code: VerifyCodeSchema,
    verify_code_api_service: VerifyCodeAPIService = Depends(),
):
    return await verify_code_api_service.exec(
        user_id=verify_code.user_id, code=verify_code.code
    )


@router.patch("/{user_id}")
async def update_verification_code(
    user_id: int,
    tg_user_id: int = Query(),
    tg_username: str = Query(),
    update_verification_code_api_service: UpdateVerificationCodeAPIService = Depends(),
):
    await update_verification_code_api_service.exec(
        user_id=user_id, tg_user_id=tg_user_id, tg_username=tg_username
    )
    return {"status": "OK"}
