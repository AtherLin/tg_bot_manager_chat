from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from data.config import support_ids
from keyboards.inline.support import support_keyboard, support_callback, cancel_support, cancel_support_callback
from loader import dp, bot


@dp.message_handler(Command("start"))
async def ask_support_call(call: types.BotCommand, state: FSMContext):
    await state.set_state("wait_in_support")
    await state.update_data(second_id=support_ids)

    await call.answer("Налаживаем свзязь...")

    keyboard = await support_keyboard(messages="many", user_id=call.from_user.id)
    for support_id in support_ids:
        support = dp.current_state(user=support_id, chat=support_id)
        if str(await support.get_state()) != "in_support":
            await bot.send_message(support_id,
                                f"С вами хочет связаться пользователь {call.from_user.full_name}",
                                reply_markup=keyboard
                                )
    for support_id in support_ids:
        if str(await support.get_state()) != "in_support": 
            await call.answer("Мы уже связались с менеджерами. Подождите некоторое время")
            return
    await call.answer("К сожалению, сейчас все менеджеры заняты. Попробуйте связаться с ними чуть позже")
        

@dp.callback_query_handler(support_callback.filter(messages="many", as_user="no"))
async def answer_support_call(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    second_id = int(callback_data.get("user_id"))
    user_state = dp.current_state(user=second_id, chat=second_id)

    if str(await user_state.get_state()) != "wait_in_support":
        await call.message.answer("К сожалению, пользователь уже передумал")
        return
    if str(await user_state.get_state()) != "in_support":
        await state.set_state("in_support")
        await user_state.set_state("in_support")
        await user_state.update_data(second_id=call.from_user.id)
        await state.update_data(second_id=second_id)

        keyboard = cancel_support(second_id)
        keyboard_second_user = cancel_support(call.from_user.id)

        await call.message.edit_text("Вы на связи с пользователем!\n"
                                    "Чтобы завершить общение нажмите на кнопку.",
                                    reply_markup=keyboard
                                    )
        await bot.send_message(second_id,
                            "менеджер на связи! Можете писать сюда свое сообщение. \n"
                            "Чтобы завершить общение нажмите на кнопку.",
                            reply_markup=keyboard_second_user
                            )


@dp.message_handler(state="wait_in_support", content_types=types.ContentTypes.ANY)
async def not_supported(message: types.Message, state: FSMContext):
    data = await state.get_data()
    second_id = data.get("second_id")

    keyboard = cancel_support(second_id)
    await message.answer("Дождитесь ответа менеджера или отмените сеанс", reply_markup=keyboard)


@dp.callback_query_handler(cancel_support_callback.filter(), state=["in_support", "wait_in_support", None])
async def exit_support(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    data = await state.get_data()
    user_id = data.get("second_id")
    second_state = dp.current_state(user=user_id, chat=user_id)
    if await second_state.get_state() is not None:
        data_second = await second_state.get_data()
        second_id = data_second.get("second_id")
        if second_id == call.from_user.id:
            await second_state.reset_state()
            await bot.send_message(user_id, "Пользователь завершил сеанс")

    await call.message.answer("Вы завершили сеанс")
    await state.reset_state()
    await second_state.reset_state()