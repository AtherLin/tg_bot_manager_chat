import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data.config import support_ids
from loader import dp

support_callback = CallbackData("ask_support", "messages", "user_id", "as_user")
cancel_support_callback = CallbackData("cancel_support", "user_id")



async def support_keyboard(messages, user_id=None):
    if user_id:
        # Есле указан второй айдишник - значит эта кнопка для оператора

        contact_id = int(user_id)
        as_user = "no"
        text = "Ответить пользователю"

    else:
        # Есле не указан второй айдишник - значит эта кнопка для пользователя
        # и нужно подобрать для него оператора

        contact_id = support_ids
        as_user = "yes"
        if messages == "many" and contact_id is None:
            # Если не нашли свободного оператора - выходим и говорим, что его нет
            return False
        text = "Написать менеджеру"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=text,
            callback_data=support_callback.new(
                messages=messages,
                user_id=contact_id,
                as_user=as_user
            )
        )
    )

    if messages == "many":
        # Добавляем кнопку завершения сеанса, если передумали звонить в поддержку
        keyboard.add(
            InlineKeyboardButton(
                text="Завершить сеанс",
                callback_data=cancel_support_callback.new(
                    user_id=contact_id
                )
            )
        )
    return keyboard


def cancel_support(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить сеанс",
                    callback_data=cancel_support_callback.new(
                        user_id=user_id
                    )
                )
            ]
        ]
    )
