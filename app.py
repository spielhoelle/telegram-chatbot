import tensorflow as tf
import tensorflow.keras
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import load_model
import os
import numpy as np

import os
import flask
import requests
from flask_apscheduler import APScheduler

VOCAB_SIZE = 88584

MAXLEN = 250
BATCH_SIZE = 64
if os.path.isfile('models/sentiment_analysis.h5') is False:
    (train_data, train_labels), (test_data,
                                test_labels) = imdb.load_data(num_words=VOCAB_SIZE)

    train_data = sequence.pad_sequences(train_data, MAXLEN)
    test_data = sequence.pad_sequences(test_data, MAXLEN)

    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(VOCAB_SIZE, 32),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])

    model.compile(loss="binary_crossentropy", optimizer="rmsprop", metrics=['acc'])

    history = model.fit(train_data, train_labels, epochs=10, validation_split=0.2)
    model.save('models/sentiment_analysis.h5')
else:
    model = load_model('models/sentiment_analysis.h5')

word_index = imdb.get_word_index()


def encode_text(text):
  tokens = tf.keras.preprocessing.text.text_to_word_sequence(text)
  tokens = [word_index[word] if word in word_index else 0 for word in tokens]
  return sequence.pad_sequences([tokens], MAXLEN)[0]


def predict(text):
  encoded_text = encode_text(text)
  pred = np.zeros((1, 250))
  pred[0] = encoded_text
  result = model.predict(pred)
  print("Answer from AI: ")
  print(result[0])
  return result[0]

app = flask.Flask(__name__, static_folder='../build', static_url_path=None)

scheduler = APScheduler()

times_run = 0
messages = []
scheduler.init_app(app)
scheduler.start()

INTERVAL_TASK_ID = 'interval-task-id'


def interval_task():
    global messages
    global times_run
    response = requests.post(
        'https://api.telegram.org/'+os.getenv("TELEGRAM_BOT_ID")+'/getUpdates', {'offset': 1})
    response.raise_for_status()
    jsonResponse = response.json()
    newMessages = []
    print("Run cronjob - messages currently in cache: ", len(messages))
    for eventuallyNewMessage in jsonResponse['result']:
        fount = [x for x in messages if x['update_id']
                 == eventuallyNewMessage['update_id']]
        if len(fount) == 0:
            print("New message")
            print(eventuallyNewMessage)
            newMessages.append(eventuallyNewMessage)

    messages = jsonResponse['result']
    if len(newMessages) > 0 and times_run != 0 and jsonResponse['result'][-1]['message'].has_key('text'):
        message = jsonResponse['result'][-1]['message']['text']

        str1 = " "
        prediction = predict(message)
        myobj = {'chat_id': '579817872',
                 'text': "Positive/negative: " + str(prediction[0])}
        if message == "yes":
            print("###########################")
            print("Bot will answer positive")
            print(" ")
            response = requests.post(
                'https://api.telegram.org/'+os.getenv("TELEGRAM_BOT_ID")+'/sendMessage', data=myobj)
        else:
            print("###########################")
            print("Bot will answer negative")
            print(" ")
            response = requests.post(
                'https://api.telegram.org/'+os.getenv("TELEGRAM_BOT_ID")+'/sendMessage', data=myobj)
    times_run += 1


scheduler.add_job(id=INTERVAL_TASK_ID, func=interval_task,
                  trigger='interval', seconds=8)

# Run the example
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
