from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from src.auth import hash_password
from src.config import VERIFICATION_SECRET_KEY
from src.models import UserModel
from src.models.verification_code import VerificationCode
from src.schemas.users import UserCreate, UserSchema
from src.schemas.verification_code import VerificationCodeSchema, VerifyCodeSchema
from src.utils import generate_six_digit_code, encode_record_id, generate_invite_link
from src.auth import create_access_token, create_refresh_token

router = APIRouter(prefix='/auth', tags=['registration'])


@router.post('/register', response_model=VerificationCodeSchema)
async def create_user(user: UserCreate):
    db_users = await UserModel.filter(username=user.username)
    db_user = db_users[0] if db_users else None

    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username is already used')

    db_user = await UserModel.create(
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db_verification_code = await VerificationCode.create(
        user_id=db_user.id,
        code=generate_six_digit_code()
    )

    db_verification_code.encode_id = encode_record_id(
        record_id=db_verification_code.id,
        secret_key=VERIFICATION_SECRET_KEY.encode()
    )

    await db_verification_code.save()
    return VerificationCodeSchema(
        id=db_verification_code.id,
        user_id=db_verification_code.user_id,
        tg_url=generate_invite_link(
            reg_hash=db_verification_code.encode_id
        )
    )


@router.post('/verify-code')
async def verify_code(verify_code: VerifyCodeSchema):
    db_user = await UserModel.get(verify_code.user_id)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User does not exist')

    if db_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User is already active')

    db_verification_code = await VerificationCode.filter(user_id=verify_code.user_id)

    if not db_verification_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Verification code not found')
    
    db_verification_code = db_verification_code[0]

    if db_verification_code.activate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification code is already used')

    normalized_db_code = str(db_verification_code.code).strip()
    normalized_input_code = str(verify_code.code).strip()

    if normalized_db_code != normalized_input_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid verification code')

    if not db_verification_code.tg_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The server did not detect tg id')

    db_verification_code.activate = True
    await db_verification_code.save()

    db_user.tg_user_id = db_verification_code.tg_user_id
    db_user.tg_username = db_verification_code.tg_username
    db_user.is_active = True
    db_user.verified_at = datetime.utcnow()
    await db_user.save()

    access_token = create_access_token(data={"sub": str(db_user.tg_user_id), "username": db_user.username, "id": db_user.id})
    refresh_token = create_refresh_token(data={"sub": str(db_user.tg_user_id), "username": db_user.username, "id": db_user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
