import csv
import re

new_dict = open('AnimeDict.txt', 'w', encoding='utf-8')
new_dict.seek(0)

with open('anime.csv', 'r', encoding='utf8') as file:
    anime_reader = csv.DictReader(file)
    for line in anime_reader:
        values = dict.values(line)
        for argument in values:
            word_list = list(argument.split())
            for word in word_list:
                added_word = re.sub('\W+', '', word)
                if 'https' in added_word:
                    continue
                else:
                    new_dict.write(added_word.lower() + ' ')

new_dict.close()

