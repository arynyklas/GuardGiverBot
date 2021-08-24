# Developer: @aryn_bots


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo.cursor import Cursor
from typing import Optional


class Keyboards:
    def __init__(self, config: dict):
        self._config = config

        self.menu = InlineKeyboardMarkup()
        self.menu.add(InlineKeyboardButton(self._config['accounts'], callback_data='accounts'))
        self.menu.add(InlineKeyboardButton(self._config['add_account'], callback_data='add_account'))

        self.to_menu = InlineKeyboardMarkup()
        self.to_menu.add(InlineKeyboardButton(self._config['to_menu'], callback_data='menu'))

        self.cancel = InlineKeyboardMarkup()
        self.cancel.add(InlineKeyboardButton(self._config['cancel'], callback_data='cancel'))

    def account(self, username: str, markup: Optional[InlineKeyboardMarkup]=InlineKeyboardMarkup()):
        markup.add(InlineKeyboardButton(username, callback_data='account_{}'.format(username)))
        return markup

    def accounts(self, accounts: Cursor):
        markup = InlineKeyboardMarkup()

        for account in accounts:
            self.account(account['username'], markup=markup)

        for row in self.to_menu.inline_keyboard:
            markup.inline_keyboard.append(row)

        return markup
