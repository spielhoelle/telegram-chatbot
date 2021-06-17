import os
import flask
import requests
from flask_apscheduler import APScheduler

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
    if len(newMessages) > 0 and times_run != 0:
        message = jsonResponse['result'][-1]['message']['text']
        myobj = {'chat_id': '579817872', 'text': ''}
        if message == "yes":
            print("###########################")
            print("Bot will answer positive")
            print(" ")
            myobj['text'] = 'Yeeeeahhhh'
            response = requests.post(
                'https://api.telegram.org/'+os.getenv("TELEGRAM_BOT_ID")+'/sendMessage', data=myobj)
        else:
            print("###########################")
            print("Bot will answer negative")
            print(" ")
            myobj['text'] = 'NOOOOOO'
            response = requests.post(
                'https://api.telegram.org/'+os.getenv("TELEGRAM_BOT_ID")+'/sendMessage', data=myobj)
    times_run += 1


scheduler.add_job(id=INTERVAL_TASK_ID, func=interval_task,
                  trigger='interval', seconds=5)

# Run the example
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
