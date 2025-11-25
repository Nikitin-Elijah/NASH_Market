from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.api_client.api_client import APIClient
from src.config import VERIFICATION_SECRET_KEY
from src.utils import escape_markdown_v2
from src.utils import decode_record_id


reg_router = Router()


@reg_router.message(Command("start"))
async def start(message: Message):
    api_client = APIClient()
    args = message.text.split()

    if len(args) > 1:
        param = args[1]

        if param.startswith("reg_"):
            reg_hash = param[4:]
            record_id = decode_record_id(
                hash_string=reg_hash, secret_key=VERIFICATION_SECRET_KEY.encode()
            )
            verification_code = await api_client.get_verification_code(
                user_id=record_id
            )

            if not verification_code["activate"]:
                code = verification_code["code"]

                user = await api_client.get_user_by_tg_user_id(
                    tg_user_id=message.from_user.id
                )

                if user:
                    await message.answer(
                        f"Добро пожаловать в телеграмм бот нашенского рынка!\n"
                        f"Этот телеграмм аккаунт уже зарегистрирован"
                    )

                else:
                    await api_client.update_verification_code(
                        user_id=record_id,
                        tg_user_id=message.from_user.id,
                        tg_username=message.from_user.username,
                    )
                    text = escape_markdown_v2(
                        f"Добро пожаловать в телеграмм бот нашенского рынка!\nКод для подтверждения регистрации:"
                    )
                    text += f"```{code}```"
                    await message.answer(text=text, parse_mode="markdownV2")

    else:
        await message.answer(f"Добро пожаловать в телеграмм бот нашенского рынка!\n")
