import requests
import json

# блок констант
HOST = "http://sandbox.rightech.io"
TOKEN = ""
# id автомата сигнал SOS
SOS_AUT=""
# id модели соответсующее защитному костюму
SUIT_MODEL_ID=""

def get_suits_id():
    # получение списка костюмов
    try:
        url = HOST+"/api/v1/objects"
        objects = requests.get(url, headers={'Authorization': "Bearer "+TOKEN})
        suits = []
        for i in json.loads(objects.text):
            if(i['model'] == SUIT_MODEL_ID):
                temp = {}
                temp[i['name']] = i['_id']
                suits.append(temp)
        return suits
    except Exception:
        return None


def get_last_messages():
    # получение списка непрочитанных сообщений
    try:
        url = HOST+"/api/v1/messages"
        messages = requests.get(url, headers={'Authorization': "Bearer "+TOKEN})
        return json.loads(messages.text)
    except Exception:
        return None


def set_read(id):
    # установить сообщение как прочитанное
    try:
        url = HOST+"/api/v1/messages/read/"+id
        requests.patch(url, headers={'Authorization': "Bearer "+TOKEN})
    except Exception:
        pass


def clear_history():
    # отчистка истории сообщений
    try:
        url = HOST+"/api/v1/messages/clear"
        requests.delete(url, headers={'Authorization': "Bearer "+TOKEN})
    except Exception:
        pass

def switch_suit(id):
    # переключение активности костюма
    try:
        url = HOST+"/api/v1/objects/"+id
        suit = requests.get(url, headers={'Authorization': "Bearer "+TOKEN})
        suit_json = json.loads(suit.text)

        suit = not suit_json['processedState']['active_state']

        url = HOST+"/api/v1/objects/"+id+"/bot/state"
        data = {"active_state": suit}
        requests.post(url, headers={'Authorization': "Bearer "+TOKEN}, data=data)
        return suit
    except Exception:
        return None


def send_sos():
    # запуск автомата SOS
    try:
        url = HOST+"/api/v1/automatons/"+SOS_AUT+"/start"
        requests.post(url, headers={'Authorization': "Bearer "+TOKEN})
    except Exception:
        return None

def get_sos_info(id):
    # состовление сообщения для сигнала SOS
    try:
        url = HOST+"/api/v1/objects/"+id
        suit = requests.get(url, headers={'Authorization': "Bearer "+TOKEN})
        suit_json = json.loads(suit.text)
        sos_info = []
        sos_info.append("Сотруднику, использующему " +
                        suit_json['name']+", требуется помощь!")
        sos_info.append("Последние координаты:")
        sos_info.append("Широта 🌎 = "+str(suit_json['processedState']['lat']))
        sos_info.append("Долгота 🌍 = "+str(suit_json['processedState']['lon']))
        sos_info.append("Высота 🌏 = "+str(suit_json['processedState']['alt']))
        sos_info.append("X 🧭 = "+str(suit_json['processedState']['x']))
        sos_info.append("Y 🧭 = "+str(suit_json['processedState']['y']))
        sos_info.append("Z 🧭 = "+str(suit_json['processedState']['z']))
        return "\n".join(sos_info)
    except Exception:
        return "Ошибка составления данных"


def get_stats(id):
    # составление сообщения для отображения статуса костюма
    try:
        url = HOST+"/api/v1/objects/"+id
        suit = requests.get(url, headers={'Authorization': "Bearer "+TOKEN})
        suit_json = json.loads(suit.text)
        stats = []
        stats.append("Заряд батареии 🔋 = " +
                    str(round((suit_json['processedState']['charge']), 1))+"%")
        stats.append("Осталось времени ⏳ = " +
                    str(round(suit_json['processedState']['remaining_time'], 1))+" минут")
        if suit_json['processedState']['active_state']:
            stats.append("Статус костюма 🦾 = Активирован ✅")
        else:
            stats.append("Статус костюма 🦾 = Деактивирован ❌")
        stats.append("Широта 🌎 = "+str(suit_json['processedState']['lat']))
        stats.append("Долгота 🌍 = "+str(suit_json['processedState']['lon']))
        stats.append("Высота 🌏 = "+str(suit_json['processedState']['alt']))
        stats.append("X 🧭 = "+str(suit_json['processedState']['x']))
        stats.append("Y 🧭 = "+str(suit_json['processedState']['y']))
        stats.append("Z 🧭 = "+str(suit_json['processedState']['z']))
        stats.append("Окружающая среда:")
        stats.append("Влажность 🧪 = " +
                    str(suit_json['processedState']['humidity'])+"%")
        stats.append("Кислород 🧪 = " +
                    str(suit_json['processedState']['oxygen'])+"%")
        stats.append("Углекислый газ 🧪 = " +
                    str(suit_json['processedState']['carbon'])+"%")
        stats.append("Оксид азота 🧪 = " +
                    str(suit_json['processedState']['nitric'])+"%")
        stats.append("Сернистый ангидрид 🧪 = " +
                    str(suit_json['processedState']['sulfurous'])+"%")
        stats.append("Сероводород 🧪 = " +
                    str(suit_json['processedState']['hydrogen_sulfide'])+"%")
        stats.append("Метан 🧪 = "+str(suit_json['processedState']['methane'])+"%")
        stats.append("Угольная пыль 🧪 = " +
                    str(suit_json['processedState']['dust'])+"%")

        return "\n".join(stats)
    except Exception:
        return "Ошибка составления данных"

