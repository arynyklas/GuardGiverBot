from aiogram import Bot, Dispatcher, types, filters, exceptions, executor
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from db import DataBase
from keyboards import Keyboards
from steam.guard import SteamAuthenticator, generate_twofactor_code
from requests.utils import dict_from_cookiejar
from steam.webauth import MobileWebAuth, CaptchaRequired, EmailCodeRequired
from config import bot_token, db_url, db_name, texts


db = DataBase(db_url, db_name)

bot = Bot(bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MongoStorage(db_name=db_name, uri=db_url))

keyboards = Keyboards(texts['keyboards'])


class UsersMiddleware(BaseMiddleware):
    def __init__(self):
        super(UsersMiddleware, self).__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.chat.type == types.ChatType.PRIVATE and not db.get_user(message.from_user.id):
            db.add_user(message.from_user.id)


class Form(StatesGroup):
    username = State()
    password = State()
    generate = State()
    captcha = State()
    email = State()
    sms = State()


@dp.callback_query_handler(state='*')
async def callback_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    args = callback_query.data.split('_')
    message = callback_query.message

    if args[0] == 'menu':
        await message.edit_text(texts['start'], reply_markup=keyboards.menu)

    elif args[0] == 'accounts':
        accounts = db.get_account(user_id=callback_query.from_user.id)
        await message.edit_text(texts['accounts'], reply_markup=keyboards.accounts(accounts))

    elif args[0] == 'add':
        if args[1] == 'account':
            await Form.username.set()
            await message.edit_text(texts['enter_username'], reply_markup=keyboards.cancel)

    elif args[0] == 'account':
        username = args[1]
        account = db.get_account(user_id=callback_query.from_user.id, username=username)

        try:
            code = generate_twofactor_code(account['sh_sc'])
            await message.edit_text(texts['account_info'].format(username=account['username'], code=code), reply_markup=keyboards.account(account['username']))
        except:
            db.delete_account(user_id=callback_query.from_user.id, username=username)
            await message.edit_text(texts['account_not_found'], reply_markup=keyboards.to_menu)

    elif args[0] == 'cancel':
        await state.finish()
        await message.edit_text(texts['cancelled'], reply_markup=keyboards.to_menu)

    await callback_query.answer()


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(texts['start'], reply_markup=keyboards.menu)


@dp.message_handler(state=Form.username)
async def process_username_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text

    await Form.password.set()
    await message.answer(texts['enter_password'], reply_markup=keyboards.cancel)


@dp.message_handler(state=Form.password)
async def process_password_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    await Form.generate.set()
    await message.answer(texts['enter_generate'], reply_markup=keyboards.cancel)


@dp.message_handler(state=Form.generate)
async def process_generate_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['generate'] = None if message.text in ['.', '-'] else message.text

        if data['generate']:
            db.add_account(message.from_user.id, data['username'], data['generate'])
            await state.finish()
            await message.answer(texts['account_added'].format(username=data['username'], rev_code=''), reply_markup=keyboards.to_menu)
            return

        msg = await message.answer(texts['wait'])

        wa = MobileWebAuth(data['username'], data['password'])

        try:
            wa.login()
            data['wa_session'] = [wa.logged_on, wa.session_id, dict_from_cookiejar(wa.session.cookies)]
        except CaptchaRequired:
            data['wa_session'] = [wa.logged_on, wa.session_id, dict_from_cookiejar(wa.session.cookies)]
            await msg.delete()
            await Form.captcha.set()
            await message.answer(texts['enter_captcha'].format(url=wa.captcha_url), reply_markup=keyboards.cancel)
        except EmailCodeRequired:
            data['wa_session'] = [wa.logged_on, wa.session_id, dict_from_cookiejar(wa.session.cookies)]
            await msg.delete()
            await Form.email.set()
            await message.answer(texts['enter_email'], reply_markup=keyboards.cancel)
        except:
            await msg.delete()
            await state.finish()
            await message.answer(texts['incorrect_data'], reply_markup=keyboards.to_menu)


@dp.message_handler(state=Form.captcha)
async def process_captcha_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['captcha'] = message.text
        wa_session = data['wa_session']
        wa = MobileWebAuth(data['username'])
        wa.logged_on = wa_session[0]
        wa.session_id = wa_session[1]
        wa.session.cookies.update(wa_session[2])

        try:
            wa.login(data['password'], captcha=data['captcha'])
            sa = SteamAuthenticator(backend=wa)
            sa.add()
        except:
            await state.finish()
            await message.answer(texts['incorrect_data'], reply_markup=keyboards.to_menu)
            return

        data['sa'] = sa

        await Form.sms.set()
        await message.answer(texts['enter_sms'], reply_markup=keyboards.cancel)


@dp.message_handler(state=Form.email)
async def process_email_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        wa_session = data['wa_session']
        wa = MobileWebAuth(data['username'])
        wa.logged_on = wa_session[0]
        wa.session_id = wa_session[1]
        wa.session.cookies.update(wa_session[2])

        try:
            wa.login(data['password'], email_code=data['email'])
            sa = SteamAuthenticator(backend=wa)
            sa.add()
        except:
            await state.finish()
            await message.answer(texts['incorrect_data'], reply_markup=keyboards.to_menu)
            return

        data['sa'] = sa

        await Form.sms.set()
        await message.answer(texts['enter_sms'], reply_markup=keyboards.cancel)


@dp.message_handler(state=Form.sms)
async def process_sms_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sms'] = message.text
        sa: SteamAuthenticator = data['sa']

        try:
            sa.finalize(data['sms'])
        except:
            await state.finish()
            await message.answer(texts['incorrect_data'], reply_markup=keyboards.to_menu)
            return

        sh_sc = sa.secrets['shared_secret']
        rev_code = sa.secrets['revocation_code']

        db.add_account(message.from_user.id, data['username'], sh_sc)
        await state.finish()
        await message.answer(texts['account_added'].format(username=data['username'], rev_code=texts['rev_code'].format(rev_code=rev_code)), reply_markup=keyboards.to_menu)


dp.middleware.setup(UsersMiddleware())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
