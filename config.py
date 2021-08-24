bot_token = '1813802062:AAEhkhBYH6yD-uHW486OqtwBHrJmiMqRkE4'

db_url = 'mongodb://localhost:27017'
db_name = 'GuardGiverBot'

texts = {
    'start': 'Привет ✌️\nC моей помощью ты можешь подключить и получать Guard коды для твоего Steam аккаунта.\nПросто нажми кнопку ниже чтобы посмотреть список аккаунтов, или же добавить аккаунт.',

    'enter_username': 'Введите логин аккаунта:',
    'enter_password': 'Введите пароль аккаунта:',
    'enter_generate': 'Введите <b>shared_secret</b> аккаунта: (если нет, отправьте точку)',
    'enter_email': 'Введите код с почты:',
    'enter_captcha': 'Введите код из <a href="{url}">капчи</a>:',

    'accounts': 'Список ваших аккаунтов:',
    'account_not_found': 'Аккаунт не найден!',

    'rev_code': 'Код для удаления: <b>{rev_code}</b>',
    'account_added': 'Аутентификатор для <code>{username}</code> добавлен!\n{rev_code}',
    'account_info': 'Информация об аккаунте:\nЛогин - <b>{username}</b>\nGuard код: <code>{code}</code>',

    'wait': 'Ожидайте',
    'incorrect_data': 'Данные введены некорректно.\nВозможно, к аккаунту не подключен телефон или меняли Steam Guard за день.\nПопробуйте ещё разок.',

    'cancelled': 'Отменено',

    'keyboards': {
        'to_menu': 'Главное меню',
        'accounts': 'Список аккаунтов',
        'add_account': 'Добавить аккаунт',
        'update': 'Обновить',
        'cancel': 'Отменить'
    }
}
