from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import VERIFICATION_SECRET_KEY
from models import VerificationCode, UserModel
from utils import decode_record_id

reg_router = Router()


@reg_router.message(Command('start'))
async def start(message: Message):
    args = message.text.split()

    if len(args) > 1:
        param = args[1]

        if param.startswith('reg_'):
            reg_hash = param[4:]
            record_id = decode_record_id(hash_string=reg_hash, secret_key=VERIFICATION_SECRET_KEY.encode())
            db_verification_code = await VerificationCode.get(record_id)

            if not db_verification_code.activate:
                code = db_verification_code.code

                db_users = await UserModel.filter(tg_user_id=message.from_user.id)
                db_user = db_users[0] if db_users else None

                if db_user:
                    await message.answer(
                        f"Добро пожаловать в телеграмм бот нашенского рынка!\n"
                        f"Этот телеграмм аккаунт уже зарегистрирован"
                    )

                else:
                    db_verification_code.tg_user_id = message.from_user.id
                    db_verification_code.tg_username = message.from_user.username
                    await db_verification_code.save()
                    await message.answer(
                        f"Добро пожаловать в телеграмм бот нашенского рынка!\n"
                        f"Код для подтверждения регистрации: {code}"
                    )

    else:
        await message.answer(
            f"Добро пожаловать в телеграмм бот нашенского рынка!\n"
        )