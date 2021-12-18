import csv
import string
import re
from spellchecker import SpellChecker
import requests
from bs4 import BeautifulSoup


# Данный блок предназначен для исправления ошибок в словах из ответов на основе словаря SpellChecker и словаря, созданного из csv файла.
spell = SpellChecker(language= 'en')
spell_rus = SpellChecker(language= 'ru')
spell.word_frequency.load_text_file('./AnimeDict.txt')

def spell_checker(words):
    checked_list = []
    misspelled = spell.unknown(words)
    checked_ok = spell.known(words)
    for word in misspelled:
        phrase = list(word.split())
        s = ''
        for item in phrase:
            s += str(spell.correction(item)) + ' '
        checked_list.append(string.capwords(s.strip()))
    for word in checked_ok:
        checked_list.append(string.capwords(word))
    return checked_list    

def spell_checker_rus(word):
    return string.capwords(spell_rus.correction(word))


# Функция ниже является вспомогательной для корректировки ответа пользователя на вопросы, подразумевающие перечисление.
# Используется для "Жанров", "Студий", "Типов" аниме.
def list_generator(user_ans):
    user_ans_list = re.split(r'[1]', re.sub('\W+', ' ', re.sub(r'[,]', '1', user_ans)))
    for item in user_ans_list: 
        item = item.strip()
    return spell_checker(user_ans_list)


# Функция корректировки пользовательского "Метража" аниме.
def user_episodes(ans):
    ans = re.sub('^\W+', '', ans)
    spell_rus.word_frequency.load_words(['многосерийное', 'полнометражное'])
    ans_checked = spell_checker_rus(ans)
    return 'Многосерийное' if (ans_checked[0] in '1МмmM') else 'Полнометражное'


# Функция корректировки пользовательской "Продолжительности" аниме.
def user_duration(time):
    duration = 0
    time = re.findall('\w+', re.sub('\W+', ' ', re.sub('\s+', ' ', time)))
    try:
        if len(time) == 1:
            duration = int(time[0])
        elif len(time) == 2:
            s = str(time[1])
            m = 1 if (s[0] in 'MmмМ') else 60
            duration = int(time[0]) * m
        elif len(time) == 3:
            s = str(time[1])
            m = 1 if (s[0] in 'MmмМ') else 60
            duration = int(time[0]) * m + int(time[2])
        elif len(time) == 4:
            s = str(time[1])
            m = 1 if (s[0] in 'MmмМ') else 60
            s = str(time[3])
            m1 = 1 if (s[0] in 'MmмМ') else 60
            duration = int(time[0]) * m + int(time[2]) * m1
        if duration == 0:
            print('Ответ введён некорректно. Попробуйте снова.')
            answer = str(input())
            ans_dict['Duration'] = user_duration(answer)
            return ans_dict['Duration']
        else:
            return str(duration)
    except:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = str(input())
        ans_dict['Duration'] = user_duration(answer)
        return ans_dict['Duration']
        


# Эта функция корректирует ответ пользователя на вопрос "Завершенности".
def user_finished(keyer):
    keyer = spell_checker_rus(re.sub('\W+', '', keyer))
    return 'True' if (string.capwords(keyer) in 'YesДа1yesда') else 'False'


# Три функции ниже корректируют исключительно числовые ответы. 
# Используются для "Годов выпуска", "Рейтинга", "Количества отзывов" аниме.
def user_years(years):
    years_list = re.findall('\d+', years)
    if len(years_list) == 2:
        return years_list
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = str(input())
        ans_dict['Years'] = user_years(answer)
        return ans_dict['Years']

def user_rating(rating):
    users_rating = re.sub(',', '.', ''.join(re.findall(r'[.,\d+]',rating)))
    if users_rating != '':
        return users_rating
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = str(input())
        ans_dict['Rating'] = user_rating(answer)
        return ans_dict['Rating']

def user_number_votes(number):
    users_number_votes = ''.join(re.findall('\d+', number))
    if users_number_votes != '':
        return users_number_votes
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = str(input())
        ans_dict['Votes'] = user_number_votes(answer)
        return ans_dict['Votes']


# Этот блок отвечает за вызовы функций по вопросам и содержит сами вопросы
def ans_func(n, ans):
    if n == 0: return list_generator(ans)
    elif n == 1: return list_generator(ans)
    elif n == 2: return list_generator(ans)
    elif n == 3: return user_episodes(ans)
    elif n == 4: return user_duration(ans)
    elif n == 5: return user_finished(ans)
    elif n == 6: return user_years(ans)
    elif n == 7: return user_rating(ans)
    elif n == 8: return user_number_votes(ans)
    else: return '<<< Ошибка >>>'

def question(n):
    if n == 0: print('Назовите интересующие жанры через запятую. Enter - если вам не важен жанр.')
    elif n == 1: print('Назовите интересующие студии через запятую. Enter - если вам не важна студия.')
    elif n == 2: print('Назовите интересующие типы аниме через запятую. Например: DVD, Movie, Music, OVA, TV, Web, Other. Enter - если тип вам не важен.')
    elif n == 3: print('Вас интересует многосерийное аниме или полнометражное? Enter - если вам не важно.')
    elif n == 4: print('Какая максимальная длительность? Enter - если вам не важна длительность.')
    elif n == 5: print('Вас интересует завершенный проект или нет? Ответьте да или нет. Enter - если вам не важно.')
    elif n == 6: print('Укажите интересуещие вас года выпуска в формате "с **** по ****". Enter - если вам не важно.')
    elif n == 7: print('Укажите минимальный рейтинг оценки от 0 до 5. Можно в дробном формате. Enter - если рейтинг вам не важен.')
    elif n == 8: print('Укажите минимальное количество отзывов. Enter - если вам не важно количество.')
    else: print('<<< Ошибка >>>')

# Блок диалогового интерфейса с пользователем.
print('Здравствуйте! Вас приветствует опросник сайта Anime-Planet!')
print('Большая просьба отвечать корректно на все вопросы, в ином случае вы не получите желаемого результата поиска(')
print('Что ж, начнем!')
ans_dict = dict.fromkeys(['Genres', 'Studios', 'Types', 'Episodes', 'Duration', 'Finished', 'Years', 'Rating', 'Votes'])
ans_keys = list(iter(ans_dict))
for num in range(len(ans_keys)):
    question(num)
    answer = str(input())
    if answer == '':
        print('<<< None >>>')
        print()
        continue
    else:
        ans_dict[ans_keys[num]] = ans_func(num, answer)
        print(ans_dict[ans_keys[num]])
print('Идёт отбор подходящих вариантов...')
print()

# Блок работы с файлом.
Chosen = []
with open('Anime2.csv', 'r', encoding='utf8') as file:
    anime_reader = csv.DictReader(file)
    for line in anime_reader:
        csv_dict = {
            'Genres': spell_checker( line['Tags'] ),
            'Studios': spell_checker( line['Studios'] ),
            'Types': spell_checker( line['Type'] ),
            'Episodes': string.capwords(line['Episodes']),
            'Duration': string.capwords(line['Duration']),
            'Finished': string.capwords(line['Finished']),
            'Years': [line['StartYear'], line['EndYear']],
            'Rating': line['Rating Score'],
            'Votes': line['Number Votes']
            }

        count = 0
        bool_key = True

        s_list = ['Genres', 'Studios', 'Types']
        for s in s_list:
            if (ans_dict[s] != None) and (csv_dict[s] != 'Unknown'):
                for item in ans_dict[s]:
                    if item in csv_dict[s]:
                        count += 1
                        break
            else:
                count += 1

        if (ans_dict['Episodes'] != None) and (csv_dict['Episodes'] != 'Unknown'):
            if (ans_dict['Episodes'] == 'Многосерийное') and (int(csv_dict['Episodes']) > 1):
                count += 1
            elif (ans_dict['Episodes'] == 'Полнометражное') and (int(csv_dict['Episodes']) == 1):
                count += 1
        else: 
            count += 1

        if (ans_dict['Duration'] != None) and (csv_dict['Duration'] != 'Unknown'):
            if int(ans_dict['Duration']) <= int(csv_dict['Duration']):
                count += 1
        else: 
            count += 1

        if (ans_dict['Finished'] != None) and (csv_dict['Finished'] != 'Unknown'):
            if ans_dict['Finished'] == csv_dict['Finished']:
                count += 1
        else: 
            count += 1

        if (ans_dict['Years'] != None) and (csv_dict['Years'] != 'Unknown'):
            if (ans_dict['Years'][0] >= csv_dict['Years'][0]) and (ans_dict['Years'][1] <= csv_dict['Years'][1]):
                count += 1
        else: 
            count += 1
        
        if (ans_dict['Rating'] != None) and (csv_dict['Rating'] != 'Unknown'):
            if ans_dict['Rating'] <= csv_dict['Rating']:
                count += 1
        elif (csv_dict['Rating'] == 'Unknown'): 
            bool_key = False
            count += 1
        else:
            count += 1
        
        if (ans_dict['Votes'] != None) and (csv_dict['Votes'] != 'Unknown'):
            if ans_dict['Votes'] <= csv_dict['Votes']:
                count += 1
        else: 
            count += 1

        if (count >= 5) and (bool_key == True):
            Chosen.append(line)

# Сортировка и запись в файл OutputFile.txt
Chosen.sort(key = lambda x: x['Rating Score'], reverse= True)
output_file = open('OutputFile.txt', 'w', encoding='utf-8')
output_file.seek(0)
output_file.write('Results' + ' : ' + str(len(Chosen)) + '\n')
output_file.write('-------------------------------' + '\n')
for i in range(len(Chosen)):
    output_file.write('Name' + ' : ' + Chosen[i]['Name'] + '\n')
    output_file.write('Alternative Name' + ' : ' + Chosen[i]['Alternative Name'] + '\n')
    output_file.write('Rating Score' + ' : ' + Chosen[i]['Rating Score'] + '\n')
    output_file.write('Synopsis' + ' : ' + Chosen[i]['Synopsis'] + '\n')
    output_file.write('Url' + ' : ' + Chosen[i]['Url'] + '\n')
    output_file.write('-------------------------------' + '\n')
output_file.close()
print('Ваша подборка в файле OutputFile.txt')
print()

# Скачивание картинок
if len(Chosen) >= 5:
    for i in range(0, 5):
        response = requests.get(Chosen[i]['Url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        img = requests.get("https://www.anime-planet.com/" + soup.find('img', class_='screenshots')['src'])
        img_file = open(str(i + 1) + '.jpg', 'wb')
        img_file.write(img.content)
        img_file.close()
    print('Постеры для ТОП-5 Аниме находятся в основной папке!')
else:
    for i in range(0, len(Chosen)):
        response = requests.get(Chosen[i]['Url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        img = requests.get("https://www.anime-planet.com/" + soup.find('img', class_='screenshots')['src'])
        img_file = open(str(i + 1) + '.jpg', 'wb')
        img_file.write(img.content)
        img_file.close()
    print('Постеры для ТОП-' + str(len(Chosen)) + ' Аниме находятся в основной папке!')