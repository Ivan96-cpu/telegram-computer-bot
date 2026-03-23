import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте переменную окружения BOT_TOKEN")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ComputerBuild(StatesGroup):
    budget = State()
    purpose = State()
    contact = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу собрать компьютер.\n"
        "Нажми /build чтобы начать"
    )


@dp.message_handler(commands=['build'])
async def cmd_build(message: types.Message):
    await ComputerBuild.budget.set()
    await message.answer(
        "💰 Какой у вас бюджет на компьютер?\n"
        "Напишите сумму в рублях:",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(state=ComputerBuild.budget)
async def process_budget(message: types.Message, state: FSMContext):
    try:
        budget = int(message.text)
        await state.update_data(budget=budget)
        await ComputerBuild.next()
        
        kb = [
            [types.KeyboardButton(text="🎮 Игры")],
            [types.KeyboardButton(text="💼 Работа/Офис")],
            [types.KeyboardButton(text="🎨 Видеомонтаж")],
            [types.KeyboardButton(text="💻 Универсальный")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        await message.answer(
            "🎯 Для каких целей собираете компьютер?",
            reply_markup=keyboard
        )
    except ValueError:
        await message.answer("Пожалуйста, введите число (только цифры)")


@dp.message_handler(state=ComputerBuild.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await ComputerBuild.next()

    kb = [
        [types.KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
        [types.KeyboardButton(text="✍️ Ввести вручную")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(
        "📞 Как с вами связаться?\n"
        "Нажмите кнопку или введите номер телефона:",
        reply_markup=keyboard
    )


@dp.message_handler(state=ComputerBuild.contact, content_types=types.ContentType.CONTACT)
async def process_contact_button(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await finish_build(message, state, phone)


@dp.message_handler(state=ComputerBuild.contact)
async def process_contact_manual(message: types.Message, state: FSMContext):
    phone = message.text
    await finish_build(message, state, phone)


async def finish_build(message: types.Message, state: FSMContext, phone: str):
    data = await state.get_data()
    build = generate_build(data['budget'], data['purpose'])

    await message.answer(
        f"✅ Ваша сборка готова!\n\n{build}\n\n"
        f"Мы свяжемся с вами по номеру: {phone}",
        reply_markup=types.ReplyKeyboardRemove()
    )

    ADMIN_ID = 1655647413
    await bot.send_message(
        ADMIN_ID,
        f"🆕 Новая заявка!\n"
        f"👤 Пользователь: @{message.from_user.username}\n"
        f"📞 Телефон: {phone}\n"
        f"💰 Бюджет: {data['budget']} руб.\n"
        f"🎯 Цель: {data['purpose']}\n\n"
        f"🖥️ Сборка:\n{build}"
    )
    await state.finish()


def generate_build(budget: int, purpose: str) -> str:
    if budget < 50000:
        return """💰 Сборка до 50000₽:
• Процессор: Intel Core i3-12100F
• Видеокарта: GTX 1650
• Материнская плата: H610M
• Оперативная память: 16GB DDR4
• SSD: 256GB NVMe
• Блок питания: 500W
• Корпус: Мини-башня"""
    elif budget < 75000:
        return """💪 Сборка базовая (популярная):
• Процессор: Intel Core i5-12400F
• Видеокарта: RTX 5060
• Материнская плата: B760
• Оперативная память: 32GB DDR4
• SSD: 512GB NVMe
• Блок питания: 750W
• Корпус: Средний башня"""
    else:
        return """🚀 Премиальная сборка:
• Процессор: Intel Core i7-13700KF
• Видеокарта: RTX 5070
• Материнская плата: B760
• Оперативная память: 32GB DDR5
• SSD: 1TB NVMe
• Блок питания: 750W
• Корпус: Полноразмерный"""


if __name__ == "__main__":
    print("🚀 Бот запускается...")
    executor.start_polling(dp, skip_updates=True)
