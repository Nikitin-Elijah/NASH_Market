from faststream.rabbit import RabbitBroker

from src.api_client.api_client import APIClient
from src.config import RABBITMQ_URL
from src.utils import bot, escape_markdown_v2


broker = RabbitBroker(url=RABBITMQ_URL)


@broker.subscriber("create_purchases")
async def purchase_notice(purchase_id: str):
    api_client = APIClient()
    purchase = await api_client.get_purchase(int(purchase_id))
    print(purchase)
    product = await api_client.get_product(int(purchase["product_id"]))
    buyer = await api_client.get_user(int(purchase["buyer_id"]))
    seller = await api_client.get_user(int(purchase["seller_id"]))
    main_image = [image for image in product["images"] if image["is_main"] == True][0]
    text = ""
    text += escape_markdown_v2("👋 Привет! У вас новое предложение 💸\n")
    text += f"_{product['name']}_\n_{product['description']}_\n"
    text += escape_markdown_v2(
        f"────────────────────────────\n{buyer['username']} желает приобрести ваш товар!\n"
    )

    if purchase["comment"]:
        text += escape_markdown_v2(f"💬 Комментарий: “{purchase["comment"]}”")

    try:
        await bot.send_photo(
            chat_id=seller["tg_user_id"],
            photo=main_image["url"],
            caption=text,
            parse_mode="markdownV2",
        )

    except Exception:
        await bot.send_message(
            chat_id=seller["tg_user_id"], text=text, parse_mode="markdownV2"
        )


@broker.subscriber("accept_purchases")
async def accept_purchase(purchase_id: str):
    api_client = APIClient()
    purchase = await api_client.get_purchase(purchase_id=int(purchase_id))
    product = await api_client.get_product(int(purchase["product_id"]))
    buyer = await api_client.get_user(int(purchase["buyer_id"]))
    seller = await api_client.get_user(int(purchase["seller_id"]))
    main_image = [image for image in product["images"] if image["is_main"] == True][0]
    text = ""
    text += escape_markdown_v2("👋 Привет! Твое предложение одобрили 💸\n")
    text += f"_{product['name']}_\n_{product['description']}_\n"
    text += escape_markdown_v2(
        f"────────────────────────────\n{seller['username']} согласен с вашим предложением о покупке!\n"
    )

    try:
        await bot.send_photo(
            chat_id=buyer["tg_user_id"],
            photo=main_image["url"],
            caption=text,
            parse_mode="markdownV2",
        )

    except Exception:
        await bot.send_message(
            chat_id=buyer["tg_user_id"], text=text, parse_mode="markdownV2"
        )


@broker.subscriber("reject_purchases")
async def reject_purchase(purchase_id: str):
    api_client = APIClient()
    purchase = await api_client.get_purchase(int(purchase_id))
    product = await api_client.get_product(int(purchase["product_id"]))
    buyer = await api_client.get_user(int(purchase["buyer_id"]))
    seller = await api_client.get_user(int(purchase["seller_id"]))
    main_image = [image for image in product["images"] if image["is_main"] == True][0]

    text = ""
    text += escape_markdown_v2("👋 Привет! Твое предложение отклонили 💸\n")
    text += f"_{product['name']}_\n_{product['description']}_\n"
    text += escape_markdown_v2(
        f"────────────────────────────\n{seller['username']} отклонил ваше предложением о покупке!\n"
    )

    try:
        await bot.send_photo(
            chat_id=buyer["tg_user_id"],
            photo=main_image["url"],
            caption=text,
            parse_mode="markdownV2",
        )

    except Exception:
        await bot.send_message(
            chat_id=buyer["tg_user_id"], text=text, parse_mode="markdownV2"
        )
