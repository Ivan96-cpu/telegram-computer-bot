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

MY_USERNAME = "TQR777"  
MY_LINK = f"https://t.me/{MY_USERNAME}"

ADMIN_ID = 1655647413

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ComputerBuild(StatesGroup):
    budget = State()
    purpose = State()
    contact = State()


@dp.message(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу собрать компьютер под ваш бюджет.\n\n"
        "📌 **Как я работаю:**\n"
        "• Если бюджет от 50 000 руб. — предложу готовую сборку\n"
        "• Если бюджет меньше 50 000 руб. — свяжу вас со мной лично\n\n"
        "Нажми /build чтобы начать"
    )


@dp.message(Command("build"))
async def cmd_build(message: types.Message, state: FSMContext):
    await state.set_state(ComputerBuild.budget)
    await message.answer(
        "💰 **Какой у вас бюджет на компьютер?**\n"
        "Напишите сумму в рублях (только цифры до 350000):",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message(ComputerBuild.budget)
async def process_budget(message: types.Message, state: FSMContext):
    try:
        budget = int(message.text)
        
        if budget <= 0:
            await message.answer("Пожалуйста, введите положительное число")
            return
            
        await state.update_data(budget=budget)
        await state.set_state(ComputerBuild.purpose)
        
        kb = [
            [types.KeyboardButton(text="🎮 Игры")],
            [types.KeyboardButton(text="💼 Работа/Офис")],
            [types.KeyboardButton(text="🎨 Видеомонтаж")],
            [types.KeyboardButton(text="💻 Универсальный")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        await message.answer(
            "🎯 **Для каких целей собираете компьютер?**\n"
            "Выберите вариант:",
            reply_markup=keyboard
        )
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число (только цифры, без пробелов и букв)")


@dp.message(ComputerBuild.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    purpose = message.text
    await state.update_data(purpose=purpose)
    await state.set_state(ComputerBuild.contact)

    kb = [
        [types.KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
        [types.KeyboardButton(text="✍️ Ввести вручную")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(
        "📞 **Как с вами связаться?**\n"
        "Нажмите кнопку или введите номер телефона:",
        reply_markup=keyboard
    )


@dp.message(ComputerBuild.contact, lambda m: m.contact is not None)
async def process_contact_button(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await finish_build(message, state, phone)


@dp.message(ComputerBuild.contact)
async def process_contact_manual(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    await finish_build(message, state, phone)


async def finish_build(message: types.Message, state: FSMContext, phone: str):
    data = await state.get_data()
    budget = data['budget']
    purpose = data['purpose']
    
    if budget < 50000:
        await message.answer(
            f"⚠️ **Бюджет {budget:,} руб. меньше минимального порога (50 000 руб.)**\n\n"
            f"К сожалению, для такого бюджета сложно собрать качественный компьютер.\n\n"
            f"✍️ **Напишите мне лично, и я помогу подобрать оптимальный вариант:**\n"
            f"👉 @{MY_USERNAME}\n\n"
            f"Или нажмите ссылку: {MY_LINK}\n\n"
            f"Обсудим ваши задачи и подберем лучшее решение! 🖥️",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        await bot.send_message(
            ADMIN_ID,
            f"⚠️ **ЗАЯВКА С МАЛЫМ БЮДЖЕТОМ!**\n\n"
            f"👤 Пользователь: @{message.from_user.username or 'нет username'}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📞 Телефон: {phone}\n"
            f"💰 Бюджет: {budget:,} руб.\n"
            f"🎯 Цель: {purpose}\n\n"
            f"❗ Бюджет меньше 50 000 руб. Нужно связаться с клиентом лично!\n"
            f"🔗 Связаться: tg://user?id={message.from_user.id}"
        )
        
    else:
        build = generate_build(budget, purpose)
        
        await message.answer(
            f"✅ **Ваша сборка готова!**\n\n"
            f"{build}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 **Бюджет:** {budget:,} руб.\n"
            f"🎯 **Цель:** {purpose}\n"
            f"📞 **Ваш контакт:** {phone}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"✍️ **Чтобы оформить заказ или уточнить детали, напишите мне:**\n"
            f"👉 @{MY_USERNAME}\n"
            f"{MY_LINK}",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        await bot.send_message(
            ADMIN_ID,
            f"🆕 **НОВАЯ ЗАЯВКА!**\n\n"
            f"👤 Пользователь: @{message.from_user.username or 'нет username'}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📞 Телефон: {phone}\n"
            f"💰 Бюджет: {budget:,} руб.\n"
            f"🎯 Цель: {purpose}\n\n"
            f"🖥️ **Сборка:**\n{build}\n\n"
            f"🔗 Связаться: tg://user?id={message.from_user.id}"
        )
    
    await state.finish()


def generate_build(budget: int, purpose: str) -> str:
    if 75000 <= budget < 90000:
        return """💰 Сборка базовая:
• Процессор: Intel Core i3-12100F
• Видеокарта: GTX 1650
• Материнская плата: H610M
• Оперативная память: 16GB DDR4
• SSD: 256GB NVMe
• Блок питания: 500W
• Корпус: Мини-башня"""
    elif 125000 <= budget < 140000:
        return """💪 Сборка популярная:
• Процессор: Intel Core i5-12400F
• Видеокарта: RTX 5060
• Материнская плата: B760
• Оперативная память: 32GB DDR4
• SSD: 512GB NVMe
• Блок питания: 750W
• Корпус: Средний башня"""
    elif 195000 <= budget < 230000:
        return """😎 Сборка флагман:
 Процессор: Intel Core i7-13700KF
• Видеокарта: RTX 5070
• Материнская плата: B760
• Оперативная память: 32GB DDR5
• SSD: 1TB NVMe
• Блок питания: 750W
• Корпус: Полноразмерный"""
    elif 317000 <= budget <= 350000:
        return """🚀 Премиальная сборка:
• Процессор: Intel Core i9-14900K
• Видеокарта: RTX 5080
• Материнская плата: Z790
• Оперативная память: 64GB DDR5
• SSD: 2TB NVMe
• Блок питания: 1000W
• Корпус: Полноразмерный"""
     else:
        return f"""⚙️ **Сборка под ваш бюджет {budget:,}₽:**...
Подберем индивидуально! Напишите мне лично: @{MY_USERNAME}

Мы подберем оптимальную конфигурацию под ваши задачи и бюджет."""


if __name__ == "__main__":
    print("🚀 Бот запускается...")
    print(f"🤖 Бот: @{MY_USERNAME}")
    executor.start_polling(dp, skip_updates=True)
