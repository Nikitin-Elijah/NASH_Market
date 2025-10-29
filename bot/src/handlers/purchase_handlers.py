from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config import database_configuration, RABBITMQ_URL
from models import PurchaseModel, ProductModel
from utils import bot, escape_markdown_v2


broker = RabbitBroker(url=RABBITMQ_URL)


@broker.subscriber('create_purchases')
async def purchase_notice(purchase_id: str):
    async with database_configuration.async_session_maker() as session:
        db_purchase = await session.scalar(
            select(PurchaseModel)
            .where(PurchaseModel.id == int(purchase_id))
            .options(
                selectinload(PurchaseModel.seller),
                selectinload(PurchaseModel.buyer),
                selectinload(PurchaseModel.product).options(
                    selectinload(ProductModel.images)
                )
            )
        )
        seller = db_purchase.seller
        buyer = db_purchase.buyer
        product = db_purchase.product
        main_image = [image for image in product.images if image.is_main == True][0]

        text = ''
        text += escape_markdown_v2('👋 Привет! У вас новое предложение 💸\n')
        text += f'_{product.name}_\n_{product.description}_\n'
        text += escape_markdown_v2(f'────────────────────────────\n{buyer.username} желает приобрести ваш товар!\n')

        if db_purchase.comment:
            text += escape_markdown_v2(f'💬 Комментарий: “{db_purchase.comment}”')

        try:
            await bot.send_photo(
                chat_id=seller.tg_user_id,
                photo=main_image.url,
                caption=text,
                parse_mode='markdownV2'
            )

        except Exception:
            await bot.send_message(
                chat_id=seller.tg_user_id,
                text=text,
                parse_mode='markdownV2'
            )


@broker.subscriber('accept_purchases')
async def accept_purchase(purchase_id: str):
    async with database_configuration.async_session_maker() as session:
        db_purchase = await session.scalar(
            select(PurchaseModel)
            .where(PurchaseModel.id == int(purchase_id))
            .options(
                selectinload(PurchaseModel.seller),
                selectinload(PurchaseModel.buyer),
                selectinload(PurchaseModel.product).options(
                    selectinload(ProductModel.images)
                )
            )
        )
        seller = db_purchase.seller
        buyer = db_purchase.buyer
        product = db_purchase.product
        main_image = [image for image in product.images if image.is_main == True][0]

        text = ''
        text += escape_markdown_v2('👋 Привет! Твое предложение одобрили 💸\n')
        text += f'_{product.name}_\n_{product.description}_\n'
        text += escape_markdown_v2(
            f'────────────────────────────\n{seller.username} согласен с вашим предложением о покупке!\n'
        )

        try:
            await bot.send_photo(
                chat_id=buyer.tg_user_id,
                photo=main_image.url,
                caption=text,
                parse_mode='markdownV2'
            )

        except Exception:
            await bot.send_message(
                chat_id=buyer.tg_user_id,
                text=text,
                parse_mode='markdownV2'
            )


@broker.subscriber('reject_purchases')
async def reject_purchase(purchase_id: str):
    async with database_configuration.async_session_maker() as session:
        db_purchase = await session.scalar(
            select(PurchaseModel)
            .where(PurchaseModel.id == int(purchase_id))
            .options(
                selectinload(PurchaseModel.seller),
                selectinload(PurchaseModel.buyer),
                selectinload(PurchaseModel.product).options(
                    selectinload(ProductModel.images)
                )
            )
        )
        seller = db_purchase.seller
        buyer = db_purchase.buyer
        product = db_purchase.product
        main_image = [image for image in product.images if image.is_main == True][0]

        text = ''
        text += escape_markdown_v2('👋 Привет! Твое предложение отклонили 💸\n')
        text += f'_{product.name}_\n_{product.description}_\n'
        text += escape_markdown_v2(
            f'────────────────────────────\n{seller.username} отклонил ваше предложением о покупке!\n'
        )

        try:
            await bot.send_photo(
                chat_id=buyer.tg_user_id,
                photo=main_image.url,
                caption=text,
                parse_mode='markdownV2'
            )

        except Exception:
            await bot.send_message(
                chat_id=buyer.tg_user_id,
                text=text,
                parse_mode='markdownV2'
            )