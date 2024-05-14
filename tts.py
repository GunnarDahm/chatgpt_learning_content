import speech_recognition as sr
import openai
import pyttsx3

# Set up OpenAI API key
openai.api_key = ""

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Define function to get response from ChatGPT
def get_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = prompt,
    max_tokens=1024,
    temperature=0.3
    )

    return response['choices'][0]['message']['content']

# creating a message history for context
message_history =[]

# Define function to convert text to audio
def say(text):
    engine.say(text)
    engine.runAndWait()

# Initialize speech recognizer
r = sr.Recognizer()

# Loop to continually capture audio and respond
while True:
    with sr.Microphone() as source:
        print("ChatGPT TTS is live. Please speak:")
        audio = r.listen(source)
        print('Processing...')

    try:
        text = r.recognize_google(audio)

        if text == 'quit':
            print('Goodbye')
            break

        else:
            print("You said: " + text)

            
            message_history.append({"role":"user",
                        "content":text})

            response = get_response(message_history)
            print('\nChat GPt Says:\n'+response)
            say(response)


    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

