import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import wikipedia
from time import time

from settings import *


with open('IDS.txt', 'r') as f:
    id_list = list(map(int, f.readlines()))


class Sc2Bot:
    def __init__(self, admin_id=0, group_id=0, chat_id=0):
        self.admin_id = admin_id
        self.group_id = group_id
        self.chat_id = chat_id

    def help_message(self):
        self.chat_message(message='Доступные команды:\n'
                                  'Помощь - возращает список команд\n'
                                  'Реши - решает введённый пример\n'
                                  'Вики - возращает краткую сводку с вики\n')

    def math_message(self):
        self.chat_message(message='Задавим их интеллектом')
        last_time = time()
        for math_event in longpoll.listen():
            if math_event.type == VkBotEventType.MESSAGE_NEW and math_event.obj.message['text'] and \
                    'reply_message' in math_event.obj.message.keys():
                try:
                    self.chat_message(message='Дело сделано: \n' +
                                              str(eval(math_event.obj.message['text'])))
                except:
                    self.chat_message(message='Упс) Что-то не так!?!')

                break

            if time() - last_time > 10:
                break

    def wiki_message(self, event):
        if 'reply_message' in event.obj.message.keys():
            try:
                self.chat_message(message='Дело сделано: \n' +
                                          str(wikipedia.summary(event.obj.message['reply_message']['text'])
                                              [:500]).split('\n')[0])
            except:
                self.chat_message(message='Упс) Ничего не найдено!?!')
        else:
            self.chat_message(message='А, чего пугаешь?')
            last_time = time()
            for wiki_event in longpoll.listen():
                if wiki_event.type == VkBotEventType.MESSAGE_NEW and wiki_event.obj.message['text'] and \
                        'reply_message' in wiki_event.obj.message.keys():
                    if 'Гриша' in wiki_event.obj.message['text'] or 'Григорий' in wiki_event.obj.message['text']:
                        self.chat_message(message='СвиноБудда мудрейший')
                        break
                    try:
                        self.chat_message(message='Дело сделано: \n' +
                                                  str(wikipedia.summary(wiki_event.obj.message['text'])
                                                      [:500]).split('\n')[0])
                    except:
                        self.chat_message(message='Упс) Ничего не найдено!?!')

                    break
                if time() - last_time > 10:
                    break

    def ls_message_with_resend(self, event):
        from_id = event.obj.message['from_id']
        text = event.obj.message['text']
        if from_id not in id_list:
            try:
                self.ls_message(user_id=from_id, message='Спасибо что написали нам, мы вам скоро ответм!?!')
                id_list.append(from_id)
                with open('IDS.txt', 'a') as f:
                    f.write('\n' + str(from_id))
            except vk_api.exceptions.ApiError:
                print('Не удалось отправить сообщение')
        self.ls_message(user_id=self.admin_id, message='Новое сообщение в сообществе с тестком:\n' + text)

    def new_post_message(self, event):
        post_id = event.object['id']
        owner_id_ = event.group_id
        wall_id = f'wall-{owner_id_}_{post_id}'
        self.chat_message(message="Новый пост в группе!", wall_id=wall_id)

    def ls_message(self, user_id=1, message=''):
        vk.messages.send(user_id=user_id,
                         message=message,
                         random_id=random.randint(0, 2 ** 64))

    def chat_message(self, message='', wall_id=''):
        vk.messages.send(
            random_id=random.randint(0, 2 ** 64),
            message=message,
            chat_id=self.chat_id,
            attachment=wall_id
        )


vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
wikipedia.set_lang("RU")


def main():
    bot = Sc2Bot(admin_id=ADMIN_ID, group_id=GROUP_ID, chat_id=CHAT_ID)
    for event in longpoll.listen():
        # сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:
            # в лс
            if event.from_user:
                bot.ls_message_with_resend(event)
            # в беседе
            if event.from_chat:
                # вики
                text = event.obj.message['text'].lower()
                if "wiki" in text or "вики" in text or "wikipedia" in text or "википедия" in text:
                    bot.wiki_message(event)
                # примеры
                if "math" in text or "реши" in text:
                    bot.math_message()
                # help
                if "help" in text or "помощь" in text:
                    bot.help_message()
        # новый пост в группе
        if event.type == VkBotEventType.WALL_POST_NEW:
            bot.new_post_message(event)


if __name__ == '__main__':
    main()