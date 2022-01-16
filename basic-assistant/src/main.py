import warnings, webbrowser as web

warnings.filterwarnings('ignore')

print('Importing tts modules ', end='\r')
import pyttsx3 as pytts

print('Importing speech_recognition', end='\r')
from speech_recognition import Recognizer, Microphone, UnknownValueError

print('Importing neuralintents     ', end='\r')
from neuralintents import GenericAssistant



print('Creating Models        ', end='\r')

recognizer = Recognizer()


speaker = pytts.init()
speaker.setProperty('rate', 150)
speaker.setProperty('voice', speaker.getProperty('voices')[0].id)

todo_list = []

def say(string: str):
    speaker.say(string)
    speaker.runAndWait()

def create_note():
    global recognizer

    say('What are the contents of the note?')

    done = False
    while not done:
        try:
            with Microphone() as mic:

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                note = recognizer.recognize_google().lower()

                say('Choose a filename.')

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                filename = recognizer.recognize_google(audio)

            with open(f'{filename}.txt', 'w') as file:
                file.write(note)
                done = True

                say(f'Successfully created the note {filename}')

        except UnknownValueError:
            recognizer = Recognizer()
            say('I did not understand that.')


def add_todo():
    global recognizer

    say('What to do to add?')

    done = False
    while not done:
        try:
            with Microphone() as mic:

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                item = recognizer.recognize_google(audio).lower()

                todo_list.append(item)
                done = True

                say(f'Successfully added item to to-do list.')
        except UnknownValueError:
            recognizer = Recognizer()
            say('I did not understand that.')

def show_todos():
    say('The items on your to do list are')
    for item in todo_list:
        say(item)


def google_this():
    global recognizer

    say('Search for')

    done = False
    while not done:
        try:
            with Microphone() as mic:

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                search = recognizer.recognize_google(audio).lower().replace(' ', '+')

                say('Googling')
                web.open(f'https://www.google.com/search?q={search}', new = 2)

        except UnknownValueError:
            recognizer = Recognizer()
            say('I did not understand that.')


def thanks():
    say('You\'re welcome. Thank you for being nice too.')

def good_robot():
    say('Thanks! I try to be. You\'re not so bad yourself.')

def hello():
    say('Hello, what can I do for you?')

def exit_assistant():
    say('Goodbye. Shutting down...')
    exit()



mappings = {
    'greeting': hello,

    'good_robot': good_robot,
    'thanks': thanks,

    'create_note': create_note,

    'add_todo': add_todo,
    'show_todos': show_todos,
    'search_google': google_this,
    'exit': exit_assistant
}

assistant = GenericAssistant('intents.json', intent_methods=mappings)

with open('intents.json') as file:
    with open('Data/old_intents.json', 'r') as old_file:
        if file.read() == old_file.read():
            assistant.load_model('Models/model')
        else:
            print('Training Models       ')
            assistant.train_model()
            assistant.save_model('Models/model')

        with open('Data/old_intents.json', 'w') as file_writer:
            file_writer.write(file.read())

print('               ')

while True:
    try:
        with Microphone() as mic:

            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recognizer.listen(mic)

            message = recognizer.recognize_google(audio).lower()

        assistant.request(message)

    except UnknownValueError:
        recognizer = Recognizer()