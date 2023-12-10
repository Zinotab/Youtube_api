import csv
from googleapiclient.discovery import build
from googletrans import Translator
import configparser
import os


config = configparser.ConfigParser()

config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
DEVELOPER_KEY = config.get('Youtube', 'api_key')
VIDEO_ID = config.get('Youtube', 'video_id')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def getComments(video_id):
    Youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    Results = Youtube.commentThreads().list(
        part="snippet",
        videoId= video_id,
        textFormat="plainText",
    ).execute()
    translator = Translator()
    comments = []
    for item in Results["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        translated_comment = translator.translate(comment)
        if translated_comment.src == 'ar':
            comments.append(comment)
    return comments

def read_words_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        words = [row[0] for row in reader]
    return words

script_directory = os.path.dirname(os.path.abspath(__file__))

positive_file_path = os.path.join(script_directory, 'Positive.csv')
negative_file_path = os.path.join(script_directory, 'Negative.csv')

positiveComments = read_words_from_csv(positive_file_path)
negativeComments = read_words_from_csv(negative_file_path)


comments = getComments(VIDEO_ID)
commentNature = {}

for comment in comments:
    contains_positive_word = any(word in comment for word in positiveComments)
    contains_negative_word = any(word in comment for word in negativeComments)
    if contains_negative_word:
        commentNature[comment] = -1
    elif contains_positive_word:  
        commentNature[comment] = 1
    else:
        commentNature[comment] = 0



file_path = os.path.join(os.path.dirname(__file__), 'comments.txt')
with open(file_path, 'w', encoding='utf-8') as file:
    i=1
    for key, value in commentNature.items():
        file.write(f"comment {i}:  {key} => {value}\n")
        i+=1
