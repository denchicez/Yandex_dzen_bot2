import logging
import threading
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
import time
import json
import datetime
id_person = ''
status_person = ''
time_person = ''
admins = set()
persons = []
status_sub = []
time_status = []
date_register = []
manager = ''
perons_channels = []
using_persons = []
class Form(StatesGroup):
    aaa = State()
    bbb = State()
    ccc = State()
    ddd = State()
    eee = State()
    fff = State()
    ggg = State()
TOKEN = ""
############################################################ скачка старых данных
try:
    with open('last_channels_status.txt', 'r',encoding='utf-8') as f:
        last_channels_status = f.read()
        last_channels_status = eval(last_channels_status)
    with open('last_states_url.txt', 'r',encoding='utf-8') as f:
        last_states_url = f.read()
        last_states_url = eval(last_states_url)
    with open('last_states_status.txt', 'r',encoding='utf-8') as f:
        last_states_status = f.read()
        last_states_status = eval(last_states_status)
except:
    last_channels_status = []
    last_states_url = []
    last_states_status = []
    print('Не найдены данные о статьях и каналах')
with open('admins.txt',encoding='utf-8') as f:
    admins_tmp = f.read()     
with open('token.txt',encoding='utf-8') as f:
    TOKEN = f.read()
    
bot =  Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

with open('info.txt',encoding='utf-8') as f:
    info_all = f.read()
with open('admins.txt',encoding='utf-8') as f:
    admins_tmp = f.read()
with open('manager.txt',encoding='utf-8') as f:
    manager = f.read()
try:
    with open('dates.txt',encoding='utf-8') as f:
        dates = f.read()
        dates = dates.split()
        for date in dates:
            date_register.append(date)
except:
    print('Дат не знаю')
try:
    with open('persons.txt',encoding='utf-8') as f:
        persons_tmp = f.read()
    persons_tmp = persons_tmp.split()
    for person in persons_tmp:
        persons.append(int(person))
except:
    print('Не помню пользователей')
try:
    with open('status_sub.txt',encoding='utf-8') as f:
        status_sub_tmp = f.read()
        status_sub_tmp = status_sub_tmp.split()
        for status in status_sub_tmp:
            status_sub.append(int(status))
except:
    print('Не помню статус пользователей')
try:
    with open('perons_channels.txt',encoding='utf-8') as f:
        perons_channels_tmp = f.read()
        perons_channels_tmp = perons_channels_tmp.split('\n')
        for channels in perons_channels_tmp:
            perons_channels.append(eval(channels))
except:
    print('Не помню канал пользователей')
try:
    with open('time_status.txt',encoding='utf-8') as f:
        time_status_tmp = f.read()
        time_status_tmp = time_status_tmp.split()
        for timer in time_status_tmp:
            time_status.append(int(timer))
except:
    print('Не помню время подписок пользователей')
admins_tmp = admins_tmp.split()
for admin in admins_tmp:
    admins.add(int(admin))    
############################################################
def get_html(url, params=None):
    r = requests.get(url, params=params)
    return r.text  
def channels_stastuses(href):
    if(get_html(href).find('<meta property="robots" content="all" />')!=-1):
        return(1)
    else:
        return(0)
def message_channel_change(status,perons_channels,status2):
    print(perons_channels[status2])
    if(status=='1'):
        return(perons_channels[status2]+' is all'+'\u2705'+'\n')
    else:
        return(perons_channels[status2]+' is none'+'\u274c'+'\n')
def get_in(html_product,text):
    index_data_begin = html_product.find(text)
    counter_open = 0
    counter_end = 0
    data_product = ''
    for index_str in range(index_data_begin+len(text)-1,len(html_product)):
        data_product = data_product + html_product[index_str]
        if(html_product[index_str]=='{'):
            counter_open+=1
        if(html_product[index_str]=='}'):
            counter_end+=1
        if(counter_open==counter_end and counter_open!=0):
            break
    return data_product
def state_stastuses(href):
    if(get_html(href).find('"isIndexable":true')!=-1):
        return(1)
    else:
        return(0)
def scrolling_states(URL,states_local_status,states_local_url,was_tried):
    if(len(states_local_status)<100 or was_tried>500):
        html = get_html(URL)
        json_html = json.loads(html)
        try:
            items = json_html["items"]
            next_url = json_html['more']['link']
            for item in items:
                was_tried = was_tried + 1
                try:
                    link = item['rawItem']["share_link"]
                    if(link.find('zen.yandex.ru/media')!=-1):
                        states_local_url.append(item['rawItem']["share_link"])
                        states_local_status = states_local_status + str(state_stastuses(item['rawItem']["share_link"]))
                except:
                    try:
                        link = item["share_link"]
                        if(link.find('zen.yandex.ru/media')!=-1):
                            states_local_url.append(item["share_link"])
                            states_local_status = states_local_status + str(state_stastuses(item["share_link"]))
                    except:
                        print('Error')
            return scrolling_states(next_url,states_local_status,states_local_url,was_tried)
        except:
            print('Статьи закончились')
            return states_local_status,states_local_url
    else:
        print('Парсер статей закончился')
        return states_local_status,states_local_url
def parse_states(href):
    states_local_status = ""
    states_local_url = list()
    was_tried = 0
    data_main_json = get_in(get_html(href),'"exportData":{')
    data_main_json = json.loads(data_main_json)
    if(len(states_local_status)<100):
        items = data_main_json["items"]
        for item in items:
            was_tried = was_tried + 1
            try:
                link = item['rawItem']["share_link"]
                if(link.find('zen.yandex.ru/media')!=-1):
                    states_local_url.append(item['rawItem']["share_link"])
                    states_local_status = states_local_status + str(state_stastuses(item['rawItem']["share_link"]))
            except:
                try:
                    link = item["share_link"]
                    if(link.find('zen.yandex.ru/media')!=-1):
                        states_local_url.append(item["share_link"])
                        states_local_status = states_local_status + str(state_stastuses(item["share_link"]))
                except:
                    print('Error')
    next_url = data_main_json['more']['link']
    return scrolling_states(next_url,states_local_status,states_local_url,was_tried)
def start_back_programm_time():
    time_start = time.time()
    k = time.time()
    while(True):
        time_end = time.time() - time_start
        if(time.time()-k>=60*30):
            k = time.time()
            for person in persons:
                index_user = persons.index(person)
                status_of_user = status_sub[index_user]
                answer = ''
                status_old_channels = last_channels_status[index_user]
                for index_channel in range(0,len(perons_channels[index_user])):
                    new_statuses, new_urls = parse_states(perons_channels[index_user][index_channel])
                    old_statuses = last_states_status[index_user][index_channel]
                    old_urls = last_states_url[index_user][index_channel]
                    status_channel_new = channels_stastuses(perons_channels[index_user][index_channel])
                    if(status_old_channels[index_channel]!=str(status_channel_new)):
                        if(status_channel_new==1):
                            answer = 'Канал '+answer + 'теперь all'+'\n'
                            if(status_of_user>0):
                                for url_index in range(0,len(new_urls)):
                                    if(old_urls.count(new_urls[url_index])>0):
                                        index_in_old = old_urls.index(new_urls[url_index])
                                        if(old_statuses[index_in_old]=='1' and new_statuses[url_index]=='0'):
                                            answer = '    '+new_urls[url_index]+'теперь none'+'\n'
                        else:
                            answer = 'Канал '+answer + 'теперь none'+'\n'
                    else:
                        if(status_channel_new==1):
                            if(status_of_user>0):
                                for url_index in range(0,len(new_urls)):
                                    if(old_urls.count(new_urls[url_index])>0):
                                        index_in_old = old_urls.index(new_urls[url_index])
                                        if(old_statuses[index_in_old]=='1' and new_statuses[url_index]=='0'):
                                            answer = '    '+new_urls[url_index]+'теперь none'+'\n'
                    last_states_url[index_user][index_channel]    = new_urls
                    last_states_status[index_user][index_channel] = new_statuses
                if(answer!=''):
                    bot.send_message(person, answer)
                print(person, '---- закончили чекать')
            if(time_end>=60*60*24):
                print('День прошел.')
                time_start = time.time()
                for time_index in range(0,len(time_status)):
                    if(time_status[time_index]!=-1):
                        time_status[time_index] = int(time_status[time_index])-1
                        if(time_status[time_index]==0):
                            status_sub[time_index]=0
                            time_status[time_index]=-1
                            perons_channels[time_index]=list()
                            bot.send_message(persons[time_index], 'У вас истекла подписка. Каналы удалены')
############################################################
@dp.message_handler(commands=['start'])
async def send_welcome(message):
     if(persons.count(message.from_user.id) == 0):
         index_user = message.from_user.id
         await message.reply(f'Я бот. Приятно познакомиться, {message.from_user.first_name}')
         tmp = message.from_user.id
         persons.append(tmp)
         now = datetime.datetime.now()
         date_today = str(now.year)+'.'+str(now.month)+'.'+str(now.day) 
         date_register.append(date_today)
         status_sub.insert(index_user,2)
         using_persons.insert(index_user,0)
         time_status.insert(index_user,95)
         last_channels_status.insert(index_user,list())
         perons_channels.insert(index_user,list()) 
         last_states_status.insert(index_user,list()) 
         last_states_url.insert(index_user,list())
     else:
         await message.reply(f'Мы с тобой уже знакомы, {message.from_user.first_name}')
         
##############################################################################
@dp.message_handler(commands=['state_status'])
async def channel_status(message):
    messages = ''
    index_user = persons.index(message.from_user.id)
    if(using_persons[index_user]==0):
        using_persons[index_user]=1
        if(len(perons_channels[index_user])>0):
            for status in range(0,len(last_channels_status[index_user])):
                if(last_channels_status[index_user][status]=='0'):
                    messages=messages+'Все статьи канала '+perons_channels[index_user][status]+' имеют статус none' + '\n'
                else:
                    tmp_message = ''
                    indexes_state_none = 0
                    for status_state_index in range(0,len(last_states_status[index_user][status])):
                        if(last_states_status[index_user][status][status_state_index]=='0'):
                            indexes_state_none = indexes_state_none+1
                            tmp_message=tmp_message+str(indexes_state_none)+'. '+last_states_url[index_user][status][status_state_index] + '\n'
                    if(tmp_message!=''):
                        messages=messages+'Канал '+perons_channels[index_user][status]+' имеет статьи со статусом none:' + '\n' + tmp_message
                    else:
                        messages=messages+'Канал '+perons_channels[index_user][status]+' не имеет статей со статусом none' + '\n'
                messages=messages+'\n'+'\n'
            await message.reply(messages)
            using_persons[index_user]=0
        else:
            await message.reply('У вас нет активных подписок')
            using_persons[index_user]=0
    else:
        await message.reply('Подождите пока выполнится другая команда.')
##############################################################################
@dp.message_handler(commands=['channel_status'])
async def state_status(message):
    messages = ''
    index_user = persons.index(message.from_user.id)
    if(using_persons[index_user]==0):
        using_persons[index_user]=1
        if(len(perons_channels[index_user])>0):
            indexes = 1
            for status in range(0,len(last_channels_status[index_user])):
                messages=messages+str(indexes)+'. '+message_channel_change(last_channels_status[index_user][status],perons_channels[index_user],status)
                indexes = indexes+1
            await message.reply(messages)
            using_persons[index_user]=0
        else:
            await message.reply('У вас нет активных подписок')
            using_persons[index_user]=0
    else:
       await message.reply('Подождите пока выполнится другая команда.')
##############################################################################         
@dp.message_handler(commands=['add'])
async def send_add_href(message):
     index_user = persons.index(message.from_user.id)
     if(using_persons[index_user]==0):
         using_persons[index_user]=1
         status_person = int(status_sub[index_user])
         try:
             if(status_person==0):
                 if(len(perons_channels[index_user])<3):
                     await Form.aaa.set()
                     await message.reply('Пришлите ссылку на канал Яндекс.Дзен, которую надо добавить')
                 else:
                     using_persons[index_user]=0
                     await message.reply('У вас привышен лимит статей! Улучшите тариф, чтобы добавить новые или удалите уже добавленные')
             if(status_person==1):
                 if(len(perons_channels[index_user])<3):
                     await message.reply('Пришлите ссылку на канал Яндекс.Дзен, которую надо добавить')
                     await Form.aaa.set()
                 else:
                     using_persons[index_user]=0
                     await message.reply('У вас привышен лимит статей! Улучшите тариф, чтобы добавить новые или удалите уже добавленные')            
             if(status_person==2):
                 if(len(perons_channels[index_user])<15):
                     await message.reply('Пришлите ссылку на канал Яндекс.Дзен, которую надо добавить')
                     await Form.aaa.set()
                 else:
                     using_persons[index_user]=0
                     await message.reply('У вас привышен лимит статей! Улучшите тариф, чтобы добавить новые или удалите уже добавленные')
             if(status_person==3):
                 if(len(perons_channels[index_user])<50):
                     await Form.aaa.set()
                     await message.reply('Пришлите ссылку на канал Яндекс.Дзен, которую надо добавить')
                 else:
                     using_persons[index_user]=0
                     await message.reply('У вас привышен лимит статей!')
         except:
             await message.reply('Пришлите ссылку на канал Яндекс.Дзен, которую надо добавить')
             await Form.aaa.set()
     else:
         await message.reply('Подождите пока выполнится другая команда.')
@dp.message_handler(state=Form.aaa, content_types=types.ContentTypes.TEXT)
async def add_href(message, state: FSMContext): #получаем ccылку на канал
    await state.finish()
    await bot.send_message(message.from_user.id, 'Нужно время для добавления каналов. Бот напишет о результатах в течении нескольких минут.');
    index_user = persons.index(message.from_user.id)
    hrefs = message.text;
    big_message = ''
    hrefs = hrefs.split()
    status_person = int(status_sub[index_user])
    for href in hrefs:
        if(href.find('yandex.ru')==-1):
            big_message = big_message+f'Неверная ссылка - {href}' + '\n'
        else:
            r = requests.get(href)
            if(r.status_code==200):
                if(status_person==0):
                    if(len(perons_channels[index_user])<3):
                        try:
                            a,b = parse_states(href)
                        except:
                            a = []
                            b = []
                        last_states_status[index_user].append(a)
                        last_states_url[index_user].append(b)
                        try:
                            last_channels_status[index_user]=last_channels_status[index_user]+str(channels_stastuses(href))
                        except:
                            last_channels_status[index_user]=str(channels_stastuses(href))
                        try:
                            hrefs_tmp = perons_channels[index_user]
                            hrefs_tmp.append(href)
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,hrefs_tmp)
                        except:
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,[href])
                        big_message = big_message+f'Подписка оформлена - {href}' + '\n'
                    else:
                        big_message = big_message+'У вас привышен лимит статей! Улучшите тариф, чтобы добавить новые или удалите уже добавленные' + '\n'
                        break
                    
                if(status_person==1):
                    if(len(perons_channels[index_user])<3):
                        try:
                            a,b = parse_states(href)
                        except:
                            a = []
                            b = []
                        last_states_status[index_user].append(a)
                        last_states_url[index_user].append(b)
                        try:
                            last_channels_status[index_user]=last_channels_status[index_user]+str(channels_stastuses(href))
                        except:
                            last_channels_status[index_user]=str(channels_stastuses(href))
                        try:
                            hrefs_tmp = perons_channels[index_user]
                            hrefs_tmp.append(href)
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,hrefs_tmp)
                        except:
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,[href])
                        big_message = big_message+f'Подписка оформлена - {href}' + '\n'
                    else:
                        big_message = big_message+'У вас привышен лимит статей! Улучшите тариф, чтобы добавить новые или удалите уже добавленные' + '\n'       
                        break
                if(status_person==2):
                    if(len(perons_channels[index_user])<15):
                        try:
                            a,b = parse_states(href)
                        except:
                            a = []
                            b = []
                        last_states_status[index_user].append(a)
                        last_states_url[index_user].append(b)
                        try:
                            last_channels_status[index_user]=last_channels_status[index_user]+str(channels_stastuses(href))
                        except:
                            last_channels_status[index_user]=str(channels_stastuses(href))
                        try:
                            hrefs_tmp = perons_channels[index_user]
                            hrefs_tmp.append(href)
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,hrefs_tmp)
                        except:
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,[href])
                        big_message = big_message+f'Подписка оформлена - {href}' + '\n'
                    else:
                        big_message = big_message+'У вас привышен лимит статей! Улучшите тариф, чтобы добавить новые или удалите уже добавленные' + '\n'
                        break
                if(status_person==3):
                    if(len(perons_channels[index_user])<50):
                        try:
                            a,b = parse_states(href)
                        except:
                            a = []
                            b = []
                        last_states_status[index_user].append(a)
                        last_states_url[index_user].append(b)
                        try:
                            last_channels_status[index_user]=last_channels_status[index_user]+str(channels_stastuses(href))
                        except:
                            last_channels_status[index_user]=str(channels_stastuses(href))
                        try:
                            hrefs_tmp = perons_channels[index_user]
                            hrefs_tmp.append(href)
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,hrefs_tmp)
                        except:
                            perons_channels.pop(index_user)
                            perons_channels.insert(index_user,[href])
                        big_message = big_message+f'Подписка оформлена - {href}' + '\n'
                    else:
                        big_message = big_message+'У вас привышен лимит статей!' + '\n'
                        break
            else:
               big_message = big_message+f'Неверная ссылка - {href}' + '\n'
    using_persons[index_user]=0
    await bot.send_message(message.from_user.id,big_message);
############################################################################## Удаление подписки
@dp.message_handler(commands=['delete'])
async def send_delete_href(message):
     if(using_persons[persons.index(message.from_user.id)]==0):
        using_persons[persons.index(message.from_user.id)]=1
        await message.reply('Пришлите ссылку на канал Яндекс.Дзен, которую надо удалить')
        await Form.bbb.set()
     else:
        await message.reply('Подождите пока выполнится другая команда.')
@dp.message_handler(state=Form.bbb, content_types=types.ContentTypes.TEXT)        
async def delete_href(message, state: FSMContext): #получаем ccылку на канал
    href = message.text;
    try:
        index_user = persons.index(message.from_user.id)
        index_href = perons_channels[index_user].index(href)
        perons_channels[index_user].remove(href)
        string_tmp = last_channels_status[index_user]
        string_tmp = string_tmp[:index_href] + string_tmp[(index_href+1):]
        last_channels_status[index_user]=string_tmp
        last_states_status[index_user]=last_states_status[index_user].pop(index_href)
        last_states_url[index_user]=last_states_url[index_user].pop(index_href)
        await bot.send_message(message.from_user.id, 'Подписка отклонена');
        await state.finish()
        using_persons[index_user]=0
    except:
        await bot.send_message(message.from_user.id, 'Вы не подписаны на такой канал');
        await state.finish()
        using_persons[index_user]=0
############################################################################## Удаление подписки
@dp.message_handler(commands=['deleteall'])
async def main_deleteall(message):
    global last_states_status
    index_user = persons.index(message.from_user.id)
    if(using_persons[index_user]==0):
        using_persons[index_user]=1
        last_states_status[index_user]=list()
        last_states_url[index_user]=list()
        last_channels_status[index_user]=list()
        perons_channels[index_user]=list()
        await message.reply('Все каналы удалены')
        using_persons[index_user]=0
    else:
        await message.reply('Подождите пока выполнится другая команда.')
############################################################################## Получить описание команд
@dp.message_handler(commands=['info'])
async def main_info(message):
    global info_all
    await message.reply(info_all)
##############################################################################   ИД ПОЛЬЗОВАТЕЛЯ
@dp.message_handler(commands=['takeid'])
async def take_id(message):
    await message.reply(message.from_user.id)
##############################################################################    АДМИН ПАНЕЛЬ
@dp.message_handler(commands=['admin_add'])
async def add_person_main(message): 
     if((message.from_user.id in admins) == True):
         await message.reply('Пришлите id пользователя')
         await Form.ccc.set()
@dp.message_handler(state=Form.ccc, content_types=types.ContentTypes.TEXT)
async def add_person_id(message): #получаем ccылку на канал
     global id_person 
     id_person = message.text
     await message.reply('Выберите статус пользователя')
     await Form.ddd.set()
@dp.message_handler(state=Form.ddd, content_types=types.ContentTypes.TEXT)
async def add_person_status(message): #получаем ccылку на канал
     global status_person
     status_person = message.text
     await bot.send_message(message.from_user.id, 'Введите через сколько дней закончится тариф')
     await Form.eee.set()
@dp.message_handler(state=Form.eee, content_types=types.ContentTypes.TEXT)
async def add_person_time(message, state: FSMContext): #получаем ccылку на канал
     try:
         index_user = persons.index(message.from_user.id)
         global time_person
         global status_person
         global id_person
         time_person = message.text
         id_person = int(id_person)
         if((persons.count(id_person))!=0):
             persons.add(id_person)
             status_sub.pop(index_user)
             status_sub.insert(index_user,status_person)
             time_status.pop(index_user)
             time_status.insert(index_user,time_person)
         else:
             persons.append(id_person)
             status_sub.insert(index_user,status_person)
             time_status.insert(index_user,time_person)
             perons_channels.insert(index_user,time_person)
         await bot.send_message(message.from_user.id, 'Подписка оформлена')
         await state.finish()
     except:
         await bot.send_message(message.from_user.id, 'Произошла ошибка')
         await state.finish()
##############################################################################
@dp.message_handler(commands=['admin_send'])
async def send_main(message): 
     if((message.from_user.id in admins) == True):
         await message.reply('Пришлите сообщение')
         await Form.fff.set()
     else:
         await message.reply('У вас нет прав')
@dp.message_handler(state=Form.fff, content_types=types.ContentTypes.TEXT)
async def send_id(message, state: FSMContext):
     messages_to_user = message.text
     for user in persons:
         await bot.send_message(user, messages_to_user)
     await state.finish()
     await message.reply('Рассылка отправлена')
##############################################################################
@dp.message_handler(commands=['admin_add_admin'])
async def add_admin_main(message): 
     if((message.from_user.id in admins) == True):
         await message.reply('Пришлите ID администратора')
         await Form.ggg.set()
     else:
         await message.reply('У вас нет прав')
@dp.message_handler(state=Form.ggg, content_types=types.ContentTypes.TEXT)
async def add_admin(message, state: FSMContext):
     admin_id = message.text
     admins.add(admin_id)
     await state.finish()
     await message.reply('Администрация добавлена')
##############################################################################
@dp.message_handler(commands=['admin_activiti'])
async def admin_activiti(message): 
     big_message = ''
     if((message.from_user.id in admins) == True):
         for person in persons:
             id_person = person
             if(len(perons_channels[persons.index(id_person)])>=1):
                 big_message = str(person)+' - имеет статус '+str(status_sub[persons.index(id_person)]) + '. До окончания подписки ему осталось ' + str(time_status[list(persons).index(id_person)]) + ' дня. '+'Пользователь был зарегестрирован -'+str(date_register[list(persons).index(id_person)])+'\n'
                 big_message = big_message + 'Подписан на каналы : '+'\n'
                 for channel in perons_channels[persons.index(id_person)]:
                     big_message = big_message+'     '+str(channel)+'\n'
             big_message = big_message+'\n'+'\n'+'\n'
         with open('activiti.txt', 'w') as f:
             f.write(big_message)
     else:
         await message.reply('У вас нет прав')
##############################################################################   ПОМОЩЬ
@dp.message_handler(commands=['help'])
async def text_help(message): 
    await bot.send_message(message.from_user.id, f'Напишите {manager}, если вам нужна помощь');
############################################################################## ПОДПИСКА
@dp.message_handler(commands=['subscribe'])
async def text_subscribe(message):
    await bot.send_message(message.from_user.id, f'Напишите {manager} , чтобы оформить подписку на бота')
##############################################################################
while True:
    try:
        my_thread = threading.Thread(target=start_back_programm_time)
        my_thread.start()
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print('Ошибочка возникла, перезапускаюсь.',e)
        with open('admins.txt', 'w') as f:
            for i in admins:
                f.write(str(i)+'\n')
        with open('persons.txt', 'w') as f:
            for i in persons:
                f.write(str(i)+'\n')
        with open('status_sub.txt', 'w') as f:
            for i in status_sub:
                f.write(str(i)+'\n')
        with open('perons_channels.txt', 'w') as f:
            k=1
            for i in perons_channels:
                if(len(perons_channels)!=k):
                    f.write(str(i)+'\n')
                else:
                    f.write(str(i))
                k=k+1
        with open('time_status.txt', 'w') as f:
            for i in time_status:
                f.write(str(i)+'\n')
        with open('last_channels_status.txt', 'w') as f:
            f.write(str(last_channels_status))
        with open('last_states_url.txt', 'w') as f:
            f.write(str(last_states_url))
        with open('last_states_status.txt', 'w') as f:
            f.write(str(last_states_url))
