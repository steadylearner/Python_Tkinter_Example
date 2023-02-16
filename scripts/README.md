# Python Audio File Test

Use these as references.

https://github.com/Uberi/speech_recognition
https://github.com/mramshaw/Speech-Recognition
https://realpython.com/playing-and-recording-sound-python/

```md
You can use to save the dependencis from requirements.txt

$pip install -r requirements.txt

You can use this to save the dependencies to requirements.txt

$pip freeze > requirements.txt
```

## Pyhton Speech Recognition

```md
Install these first

$brew install portaudio
$brew install flac ($apt-get install flac) 

and test the command with "I am a steady learner"

$python scripts/test_speech_recognition.py
```

## Python Record Audio to a file

Use this if you want to test with your own audio files.

```md
and test the command with "I am a steady learner"

$python scripts/test_record_sound.py
```

## Use pyttsx and no need to save files

```py
# https://github.com/nateshmbhat/pyttsx3

# language  : 

# for voice in engine.getProperty('voices'):
#     print(voice)

# gender    : VoiceGenderFemale, VoiceGenderMale
import pyttsx3

def change_voice(engine, language, gender='VoiceGenderFemale'):
    for voice in engine.getProperty('voices'):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))

engine = pyttsx3.init()
change_voice(engine, "en_US", "VoiceGenderFemale")

what_you_typed = input("Type something?\n")
engine.say(f"You typed {what_you_typed}")

engine.runAndWait()
```

https://github.com/nateshmbhat/pyttsx3

