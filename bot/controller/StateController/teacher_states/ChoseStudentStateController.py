from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.controller.StateController.States import States
from bot.loader import dp
from bot.repository.StateInfoRepository import StateInfoRepository
from bot.repository.UserRepository import UserRepository
from utils.injector import StateController, ChangeState


@StateController(States.chose_student, dp)
class ChoseStudentStateController:

    stateInfoRepository = StateInfoRepository
    userRepository = UserRepository

    RESULTS = "Результаты"
    FULL_STAT = "Полная статистика"
    CHOOSE_STUDENT = "Ученики ▸"
    BACK = "◂ Назад"

    CHOOSE_STUDENT_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True)
    for student in userRepository.get_all_students():
        CHOOSE_STUDENT_KEYBOARD.add(KeyboardButton(f"{student} ▸"))
    CHOOSE_STUDENT_KEYBOARD.add(KeyboardButton(BACK))

    @classmethod
    async def handler(cls, message: types.Message):

        if message.text == cls.BACK:
            await ChangeState(States.teacher_menu, message)
            return

        text = message.text.split()
        if len(text) == 2 and await cls.userRepository.is_student(text[0]):
            cls.stateInfoRepository.get(message.from_user.id).chosen_student = text[0]
            await ChangeState(States.chose_task, message)
        else:
            await message.answer("Я вас не понял, пожалуйста воспользуйтесь кнопкой из клавиатуры")

    @classmethod
    async def prepare(cls, message: types.Message):
        await message.answer(cls.CHOOSE_STUDENT, reply_markup=cls.CHOOSE_STUDENT_KEYBOARD)
