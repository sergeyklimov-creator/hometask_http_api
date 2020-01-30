import requests
import os

API_KEY = \
    'trnsl.1.1.20200126T054625Z.88e7966dda452db5.eb5f3f3cbd027071eeab928892e4003aee58a923' 
URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate' 
TOKEN_DISK = 'AgAAAAAT8nZtAADLW9ZsC2S7eUxhmCZVRpo9zns' 
URL_DISK = 'https://cloud-api.yandex.net/v1/disk/resources/upload' 

# default folder
FROM_PATH = 'source' 
TO_PATH = 'translation' 

def get_source_text(lang, path='.'): 
    '''
    open the source file, returning the text
    '''    
    with open(os.path.join(path, lang.upper()+'.txt')) as file: 
       text = file.read() 
    
    return text 

def write_target_text(text, lang='ru', path='.'): 
    '''
    write the translated text to the file    
    '''
    with open(os.path.join(path, lang.upper()+'.txt'), 'w', encoding='utf-8') as file: 
       file.write(text)     

def write_yandex_disk(lang='ru', path='.'): 
    '''
    writing a file to the cloud 
    '''
    
    headers = { 
        'Accept': 'application/json', 
        'Content-Type': 'application/json', 
        'Authorization': TOKEN_DISK, 
    } 

    params = {         
        'path': f'Netology/{lang.upper()}.txt', 
        'overwrite': True,         
    } 

    resp_json = requests.get(URL_DISK, headers=headers, params=params).json()     
    
    with open (os.path.join(path, lang.upper()+'.txt')) as file: 
        resp_put = requests.put(resp_json['href'], file.read().encode('utf-8'))
    
    return resp_put.status_code

def translate(text, from_lang, to_lang='ru'): 
    '''
    translate text using the API 
    '''    
    params = { 
        'key': API_KEY, 
        'lang': f'{from_lang}-{to_lang}', 
    } 
    data = { 
        'text': text 
    } 
    resp_json = requests.post(URL, params=params, data=data).json() 
    return resp_json['text'][0] if resp_json['code'] == 200 else None 

def files_list(path='.'): 
    '''
    We make a list of languages in which the source files are written. By file names 
    '''
    try:
        return [foo[:-4].lower() for foo in os.listdir(os.path.join(path)) if foo.endswith('.txt')] 
    except:
        return []

def exist_lang(lang):

    params = { 
        'key': API_KEY, 
        'ui': 'ru', 
    }     
    resp_json = requests.post('https://translate.yandex.net/api/v1.5/tr.json/getLangs', params=params).json()
    return True if lang in resp_json['langs'].keys() else False

if __name__ == '__main__':     

    print('ПРОГРАММА-ПЕРЕВОДЧИК\nВведите исходные данные:') 
    
    from_path = input(f'  Папка исходных текстов (Enter - {FROM_PATH}): ').strip().lower()
    if not from_path: from_path = FROM_PATH 
    if files_list(from_path) == []:
        raise ValueError(f'Папка {from_path} либо пуста, либо не существует')

    to_path = input(f'  Папка файлов с результатами (Enter - {TO_PATH}): ').strip().lower()    
    if not to_path: to_path = TO_PATH
    if to_path not in os.listdir():
        raise ValueError(f'Указанной папки {to_path} для файлов с результатами не существует')

    print(f'\nВ папке {from_path} для перевода доступны статьи на следующих языках: {files_list(from_path)}')    

    from_lang = input(f'\n  Язык с которого перевести (два символа): ').strip().lower() 
    to_lang = input(f'  Язык на который перевести (Enter - русский): ').strip().lower() 

    if not to_lang: to_lang = 'ru' 

    if from_lang not in files_list(from_path):
        raise ValueError(f'Исходных текстов на языке {from_lang} в папке {from_path} нет')
    if not exist_lang(to_lang):
        raise ValueError(f'Вы указали несуществующее обозначение языка {to_lang} на который хотите перевести')

    source_text = get_source_text(from_lang, from_path) 
    write_target_text(translate(source_text, from_lang, to_lang), to_lang, to_path) 

    print('\nПеревод выполнен') 

    to_cloud = input('  Выложить файл в облако (''y'' - да, Enter - завершить работу программы): ') .strip()  
    if to_cloud == 'y':
        if write_yandex_disk(lang=to_lang, path=to_path) == 201:
            print('  Файл с переводом выложен в облако https://disk.yandex.ru/client/disk/Netology')
