from aiogram import types
from aiogram.types import KeyboardButton, ParseMode, ReplyKeyboardMarkup
from bot.controller.States import HelpMenu, StudentMenu, WaitAuth
from bot.model.User import User
from bot.repository.StateInfoRepository import StateInfoRepository
from bot.repository.UserRepository import UserRepository
from bot.service.TokenService import TokenService
from bot.teletrik.Controller import Controller
from bot.teletrik.DI import controller


@controller(HelpMenu)
class HelpMenuStateController(Controller):
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
        state_info_repository: StateInfoRepository,
    ):
        self.user_repository: UserRepository = user_repository
        self.token_service: TokenService = token_service
        self.state_info_repository: StateInfoRepository = state_info_repository

    MAIN_MENU = "◂ Главное меню"
    AUTH = "Сменить кабинет ▸"
    REMEMBER = "Напомнить токен"
    HOW_TO_SUBMIT = "ℹ️ Как сдать задачу"
    HOW_TO_CHECK_RESULT = "ℹ️ Как узнать результат"
    HOW_TO_LEKTORIUM = "ℹ️ Информация для Лекториума"
    HOW_TO_UNDERSTAND_RESULT_SUBMIT = "ℹ️ Что означают + - ?"
    HOW_TO_UNDERSTAND_RESULT_TASK = "ℹ️ Что означают ✅ ❌ 🔄"

    CHOOSE_ACTION = "Выберите действие, нажав нужную кнопку"

    HELP_MENU_KEYBOARD = ReplyKeyboardMarkup()
    HELP_MENU_KEYBOARD.add(
        KeyboardButton(MAIN_MENU),
        KeyboardButton(AUTH),
        KeyboardButton(REMEMBER),
        KeyboardButton(HOW_TO_SUBMIT),
        KeyboardButton(HOW_TO_CHECK_RESULT),
        KeyboardButton(HOW_TO_LEKTORIUM),
        KeyboardButton(HOW_TO_UNDERSTAND_RESULT_SUBMIT),
        KeyboardButton(HOW_TO_UNDERSTAND_RESULT_TASK),
    )

    async def handle(self, message: types.Message):

        match message.text:

            case self.AUTH:
                return WaitAuth

            case self.MAIN_MENU:
                tg_id: str = message.from_user.id
                user: User | None = await self.user_repository.get_by_telegram_id(tg_id)

                if user is None:
                    token: str = self.token_service.generate_new_token(tg_id)
                    await self.user_repository.create_user(token, "student", tg_id)
                    self.state_info_repository.create(
                        message.from_user.id, token
                    )
                    return StudentMenu
                else:
                    self.state_info_repository.create(
                        message.from_user.id, user.user_id
                    )
                    return StudentMenu

            case self.REMEMBER:
                tg_id: str = message.from_user.id
                user: User | None = await self.user_repository.get_by_telegram_id(tg_id)

                if user is None:
                    await message.answer(
                        "Вы ещё не зарегестрированы, для регистрации отправьте /start"
                    )
                else:
                    await message.answer("Ваш токен:")
                    await message.answer(user.user_id)
                return HelpMenu

            case self.HOW_TO_SUBMIT:
                await message.answer(
                    """*Как сдать задачу?*
1. В появившемся после авторизации меню нажмите на кнопку с задачей, решение на которую собираетесь отправить.
2. Нажмите на `Отправить▸`.
3. Прикрепите файл с решением и отправьте его боту.
4. В ответ вы получите id вашего решения, по которому вы сможете узнать результат.""",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return HelpMenu
            case self.HOW_TO_CHECK_RESULT:
                await message.answer(
                    """*Как узнать результат?*
1. В появившемся после авторизации меню вы можете увидеть итоговый результат по каждой задаче.
2. Если вы хотите узнать результат по конкретному решению, то нажмите на кнопку с соответсвующей задачей.
3. Нажмите на `Попытки`.
4. В ответ вы получите таблицу с результатом проверки по каждому отправленному решению.""",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return HelpMenu
            case self.HOW_TO_LEKTORIUM:
                await message.answer(
                    """*Как узнать информацию для Лекториума?*
1. Нажмите на кнопку с задачей, за которую у вас стоит ✅.
2. Нажмите на кнопку `Данные для Лектоиума`. Бот вам ответит сообщением, которое содержит "hash" и "pin".
3. Скопируйте "hash" и "pin" и введите в соответсвующие поля на сайте Лекториума.""",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return HelpMenu
            case self.HOW_TO_UNDERSTAND_RESULT_SUBMIT:
                await message.answer(
                    """*Статусы решений*
⚬ `+` — решение правильное.
⚬ `-` — решение неправильное.
⚬ `?` — решение тестируется.""",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return HelpMenu
            case self.HOW_TO_UNDERSTAND_RESULT_TASK:
                await message.answer(
                    """*Статусы задач*
Если было отправлено хотя бы одно решение, вы сможете увидеть один из следующих статусов:
⚬ ✅ — если было отправлено хотя бы одно правильное решение.
⚬ ❌ — если правильных решений нет.
⚬ 🔄 — если правильных решений нет, но есть решения, которые тестируются.""",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return HelpMenu
            case _:
                await message.answer(
                    "Я Вас не понял, пожалуйста воспользуйтесь кнопкой из клавиатуры"
                )
                return HelpMenu

    async def prepare(self, message: types.Message):
        await message.answer(self.CHOOSE_ACTION, reply_markup=self.HELP_MENU_KEYBOARD)
