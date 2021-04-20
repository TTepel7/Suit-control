import telebot
import os
import json
import rig
from keyboa import Keyboa
from telebot import types
import threading
import time
# token для телеграм бота
te_bot = telebot.TeleBot('')

# получения информации о пользователях из JSON файла
users = {}
if os.path.exists('users.json'):
    with open('users.json') as f:
        file_content = f.read()
        users = json.loads(file_content)


def notification():
    # отправка уведомлений раз в секунду
    rig.clear_history()
    # список сообщений которые отправляются только владельцу костюма
    singlecast_messages = ['Вне геозоны проведения работ',
                           'В геозоны проведения работ', 'В безопасности', 'В опасной геозоне', 'Низкий уровень заряда']
    while True:
        try:
            messages = rig.get_last_messages()
            for m in messages:
                if m['message-body'] == "Необходима помощь!":
                    sos_mes = rig.get_sos_info(m['id'])
                    for user_id in users.keys():
                        te_bot.send_message(user_id, sos_mes)
                elif(m['message-body'] in singlecast_messages):
                    for user_id, user_data in users.items():
                        if user_data['notif'] == False:
                            pass
                        elif user_data['object_id'] == m['object']:
                            te_bot.send_message(user_id, m['message-body'])
                else:
                    for user_id, user_data in users.items():
                        if user_data['notif'] == True:
                            te_bot.send_message(user_id, m['message-body'])
                rig.set_read(m['_id'])
        except Exception:
            rig.clear_history()
        time.sleep(1)


@te_bot.message_handler(content_types=['text'])
def get_text_messages(message):
    try:
        if message.text.lower() == '/start':
            # обработка команды начала работы
            markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
            status_b = types.KeyboardButton('Запросить статус костюма 📡')
            notif_b = types.KeyboardButton('Включить/Отключить уведомления 🔔')
            suit_enable_b = types.KeyboardButton('Включить/Отключить костюм 🔛')
            sos_b = types.KeyboardButton('Подать сигнал помощи 🆘')
            markup.row(status_b)
            markup.row(notif_b, suit_enable_b)
            markup.row(sos_b)
            te_bot.send_message(
                message.from_user.id, 'Здравствуйте, это чат бот для управления защитным костюмом на шахте.', reply_markup=markup)
            kb_suits = Keyboa(items=rig.get_suits_id()).keyboard
            te_bot.send_message(
                message.from_user.id, 'Для начала работы необходиимо пройти процедуру выбора костюма.', reply_markup=kb_suits)
        elif message.text == 'Включить/Отключить уведомления 🔔':
            # отключение/включение всех уведомлений кроме SOS
            users[str(message.from_user.id)]['notif'] = not users[str(
                message.from_user.id)]['notif']
            with open('users.json', 'w') as f:
                json.dump(users, f)
            if users[str(message.from_user.id)]['notif']:
                te_bot.send_message(message.from_user.id, 'Уведомления включены')
            else:
                te_bot.send_message(message.from_user.id, 'Уведомления выключены')
        elif message.text == 'Запросить статус костюма 📡':
            stats = rig.get_stats(users[str(message.from_user.id)]['object_id'])
            te_bot.send_message(message.from_user.id, stats)
        elif message.text == "Включить/Отключить костюм 🔛":
            suit = rig.switch_suit(users[str(message.from_user.id)]['object_id'])
            if suit:
                te_bot.send_message(message.from_user.id, "Костюм активирован")
            else:
                te_bot.send_message(message.from_user.id, "Костюм деактивирован")
        elif message.text == "Подать сигнал помощи 🆘":
            rig.send_sos()
            te_bot.send_message(message.from_user.id,
                                "Сигнал о помощи подан, ожидайте!")
        else:
            te_bot.send_message(message.from_user.id,
                                'Не понимаю, что это значит.')
    except Exception:
        print('Ошибка при обработке сообщений')


@te_bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # регистрация выбранного костюма
    try:
        users[str(call.from_user.id)] = {'object_id': call.data, 'notif': True}
        with open('users.json', 'w') as f:
            json.dump(users, f)
        te_bot.send_message(call.from_user.id,'Id сохранен, можете приступать к работе')
    except Exception:
        print("Ошибка при сохранении файла")

# запуск прослушки сообщений от телеграмма, а так же потока отправки уведомлений
t = threading.Thread(target=notification)
t.start()
te_bot.polling(none_stop=True)