import csv
import string
import re
from spellchecker import SpellChecker
import requests
from bs4 import BeautifulSoup

# Данный блок предназначен для исправления ошибок в словах из ответов 
# на основе словаря SpellChecker 
# и словаря, созданного из csv файла.
spell = SpellChecker(language='en')
spell_rus = SpellChecker(language='ru')
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


# Функция ниже является вспомогательной для корректировки 
# ответа пользователя на вопросы, подразумевающие перечисление.
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


# Эта функция корректирует ответ пользователя на вопрос "Завершенности".
def user_finished(keyer):
    keyer = spell_checker_rus(re.sub('\W+', '', keyer))
    return 'True' if (string.capwords(keyer) in 'YesДа1yesда') else 'False'


# 4 функции ниже корректируют исключительно числовые ответы.
# Используются для "Годов выпуска", "Рейтинга", 
# "Количества отзывов", "Продолжительности" аниме.
def user_years(years):
    years_list = re.findall('\d+', years)
    if len(years_list) == 2:
        return years_list
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = input()
        ans_dict['Years'] = user_years(answer)
        return ans_dict['Years']


def user_rating(rating):
    users_rating = re.sub(',', '.', ''.join(re.findall(r'[.,\d+]', rating)))
    if users_rating != '':
        return users_rating
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = input()
        ans_dict['Rating'] = user_rating(answer)
        return ans_dict['Rating']


def user_number_votes(number):
    users_number_votes = ''.join(re.findall('\d+', number))
    if users_number_votes != '':
        return users_number_votes
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = input()
        ans_dict['Votes'] = user_number_votes(answer)
        return ans_dict['Votes']


def user_duration(time):
    duration = ''.join(re.findall('\d+', time))
    if duration != '':
        return duration
    else:
        print('Ответ введён некорректно. Попробуйте снова.')
        answer = input()
        ans_dict['Duration'] = user_duration(answer)
        return ans_dict['Duration']


# Этот блок отвечает за вызовы функций по вопросам и содержит сами вопросы
def ans_func(n, ans):
    if n == 0:
        return list_generator(ans)
    elif n == 1:
        return list_generator(ans)
    elif n == 2:
        return list_generator(ans)
    elif n == 3:
        return user_episodes(ans)
    elif n == 4:
        return user_duration(ans)
    elif n == 5:
        return user_finished(ans)
    elif n == 6:
        return user_years(ans)
    elif n == 7:
        return user_rating(ans)
    elif n == 8:
        return user_number_votes(ans)
    else:
        return '<<< Ошибка >>>'


def question(n):
    if n == 0:
        print('Назовите интересующие жанры через запятую. Enter - если вам не важен жанр.')
    elif n == 1:
        print('Назовите интересующие студии через запятую. Enter - если вам не важна студия.')
    elif n == 2:
        print(
            'Назовите интересующие типы аниме через запятую. Например: DVD, Movie, Music, OVA, TV, Web, Other. Enter '
            '- если тип вам не важен.')
    elif n == 3:
        print('Вас интересует многосерийное аниме или полнометражное? Enter - если вам не важно.')
    elif n == 4:
        print('Какая максимальная длительность в минутах? Enter - если вам не важна длительность.')
    elif n == 5:
        print('Вас интересует завершенный проект или нет? Ответьте да или нет. Enter - если вам не важно.')
    elif n == 6:
        print('Укажите интересуещие вас года выпуска в формате "с **** по ****". Enter - если вам не важно.')
    elif n == 7:
        print(
            'Укажите минимальный рейтинг оценки от 0 до 5. Можно в дробном формате. Enter - если рейтинг вам не важен.')
    elif n == 8:
        print('Укажите минимальное количество отзывов. Enter - если вам не важно количество.')
    else:
        print('<<< Ошибка >>>')


def is_serial(answer, csv_entry):
    if answer == 'Полнометражное' and int(csv_entry) == 1:
        return True
    else:
        return False


def is_full_length(answer, csv_entry):
    if answer == 'Многосерийное' and int(csv_entry) > 1:
        return True
    else:
        return False


# Блок диалогового интерфейса с пользователем.
print('Здравствуйте! Вас приветствует опросник сайта Anime-Planet!')
print('Большая просьба отвечать корректно на все вопросы, в ином случае вы не получите желаемого результата поиска(')
print('Что ж, начнем!')
ans_dict = dict.fromkeys(['Genres', 'Studios', 'Types', 'Episodes', 'Duration', 'Finished', 'Years', 'Rating', 'Votes'])
ans_keys = list(iter(ans_dict))
for num in range(len(ans_keys)):
    question(num)
    answer = input()
    if answer == '':
        print('<<< None >>>\n')
        continue
    else:
        ans_dict[ans_keys[num]] = ans_func(num, answer)
        print(ans_dict[ans_keys[num]])
print('Идёт отбор подходящих вариантов...\n')

# Блок работы с файлом.
chosen = []
with open('Anime2.csv', 'r', encoding='utf8') as file:
    anime_reader = csv.DictReader(file)
    for line in anime_reader:
        csv_dict = {
            'Genres': spell_checker(line['Tags']),
            'Studios': spell_checker(line['Studios']),
            'Types': spell_checker(line['Type']),
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
            if (ans_dict[s] is not None) and (csv_dict[s] != 'Unknown'):
                for item in ans_dict[s]:
                    if item in csv_dict[s]:
                        count += 1
                        break
            else:
                count += 1
        
        labels = ['Episodes', 'Duration', 'Finished', 'Years', 'Rating', 'Votes']

        for label in labels:
            answer = ans_dict[label]
            csv_entry = csv_dict[label]
            if (answer is None) or (csv_entry == 'Unknown'):
                if (label == 'Rating') and (csv_entry == 'Unknown'):
                    bool_key = False
                count += 1
            else:
                if label == 'Episods':
                    if (is_serial(answer, csv_entry) or
                        is_full_length(answer, csv_entry)):
                        count += 1
                elif label == 'Duration':
                    if int(answer) <= int(csv_entry):
                        count += 1
                elif label == 'Finished':
                    if answer == csv_entry:
                        count += 1
                elif label == 'Years':
                    if ((answer[0] >= csv_entry[0]) and 
                        (answer[1] <= csv_entry[1])):
                        count += 1
                elif label == 'Rating':
                    if answer <= csv_entry:
                        count += 1
                elif label == 'Votes':
                    if answer <= csv_entry:
                        count += 1

        if (count >= 5) and bool_key:
            chosen.append(line)

# Сортировка и запись в файл OutputFile.txt
chosen.sort(key=lambda x: x['Rating Score'], reverse=True)
output_file = open('OutputFile.txt', 'w', encoding='utf-8')
output_file.seek(0)
output_file.write('Results' + ' : ' + str(len(chosen)) + '\n')
output_file.write('-------------------------------' + '\n')
for i in range(len(chosen)):
    output_file.write('Name' + ' : ' + chosen[i]['Name'] + '\n')
    output_file.write('Alternative Name' + ' : ' + chosen[i]['Alternative Name'] + '\n')
    output_file.write('Rating Score' + ' : ' + chosen[i]['Rating Score'] + '\n')
    output_file.write('Synopsis' + ' : ' + chosen[i]['Synopsis'] + '\n')
    output_file.write('Url' + ' : ' + chosen[i]['Url'] + '\n')
    output_file.write('-------------------------------' + '\n')
output_file.close()
print('Ваша подборка в файле OutputFile.txt\n')

# Скачивание картинок
if len(chosen) >= 5:
    for i in range(0, 5):
        response = requests.get(chosen[i]['Url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        img = requests.get("https://www.anime-planet.com/" + soup.find('img', class_='screenshots')['src'])
        img_file = open(str(i + 1) + '.jpg', 'wb')
        img_file.write(img.content)
        img_file.close()
    print('Постеры для ТОП-5 Аниме находятся в основной папке!')
else:
    for i in range(0, len(chosen)):
        response = requests.get(chosen[i]['Url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        img = requests.get("https://www.anime-planet.com/" + soup.find('img', class_='screenshots')['src'])
        img_file = open(str(i + 1) + '.jpg', 'wb')
        img_file.write(img.content)
        img_file.close()
    print('Постеры для ТОП-' + str(len(chosen)) + ' Аниме находятся в основной папке!')