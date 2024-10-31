
# There is a data issue and I haven't found out where it's coming from yet. some words are not showing up when they're supposed to


from deep_translator import GoogleTranslator
import sqlite3


language_codes = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'assamese': 'as', 'aymara': 'ay', 'azerbaijani': 'az', 'bambara': 'bm', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bhojpuri': 'bho', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dhivehi': 'dv', 'dogri': 'doi', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'guarani': 'gn', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'konkani': 'gom', 'korean': 'ko', 'krio': 'kri', 'kurdish (kurmanji)': 'ku', 'kurdish (sorani)': 'ckb', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg', 'luxembourgish': 'lb', 'macedonian': 'mk', 'maithili': 'mai', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'meiteilon (manipuri)': 'mni-Mtei', 'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia (oriya)': 'or', 'oromo': 'om', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'quechua': 'qu', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'sanskrit': 'sa', 'scots gaelic': 'gd', 'sepedi': 'nso', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'tigrinya': 'ti', 'tsonga': 'ts', 'turkish': 'tr', 'turkmen': 'tk', 'twi': 'ak', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}

language_codes = list(language_codes.values())

connection = sqlite3.connect("lang.db.sqlite3")
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS words (en_words text);""")
upper_chars = set("QWERTYUIOPASDFGHJKLZXCVBNM")
file = open("/usr/share/dict/american-english", "r").read().split("\n")[:-1]
words = [w for w in file if w[0] not in upper_chars and "'" not in w]
for word in words:
    cursor.execute("INSERT INTO words (en_words) VALUES (?)", [word])

cursor.execute("CREATE UNIQUE INDEX en_words_idx on words(en_words);")

import time
connection.commit()
print("added all english words")
words = ".".join(words)
for lang_code in language_codes:
    print("doing language code", lang_code)
    try:
        cursor.execute("ALTER TABLE words ADD COLUMN " + lang_code + "_words text;")
    except:
        pass
    start = 0
    # this next line is an off by 1 error
    for index in range(len(words)//5000):
        if lang_code == 'ca' and index <  47:
            pass
        else:
            time.sleep(1)
            print(index, "of", len(words)//5000)
            end = words.rfind(".", start, start + 5000)
            if end == -1:
                end = len(words)
            write_this = words[start:end]
            start = end + 1
            translated = GoogleTranslator(source='auto', target=lang_code).translate(write_this)
            to_add = zip(translated.split("."), write_this.split("."))
            for pair in to_add:
                try:
                    cursor.execute("UPDATE words set " + lang_code + "_words = ? WHERE en_words = ?;", pair)
                except:
                    pass
            connection.commit()


connection.commit()
