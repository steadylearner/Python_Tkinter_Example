[You can follow me at GitHub.]: https://github.com/steadylearner

[You can contact or hire me at Telegram.]: https://t.me/steadylearner

[python_audio]: https://github.com/steadylearner/python_audio

In this post, we will learn how to make a simple CLI translator with Python. You can use it to learn a language or test translator service etc.

Before we start, please install Python and pip if you haven't yet. Then, read the docs for the packages we will use.

1. [How to install Python](https://realpython.com/installing-python/)

2. [How to install pip](https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/)

3. [pyttsx3 to hear voice along with text](https://github.com/nateshmbhat/pyttsx3)

4. [deep-translator to translate your CLI input](https://github.com/nidhaloff/deep-translator)

Then, save a file with the code below after you install them with this.

```console
$pip install pyttsx3 deep_translator
```

You can use $touch test_text.py or something else for your file name.

```py
import pyttsx3
from deep_translator import GoogleTranslator

def change_voice(engine, language, gender='VoiceGenderFemale'):
    for voice in engine.getProperty('voices'):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError(
        "Language '{}' for gender '{}' not found".format(language, gender))


engine = pyttsx3.init()
change_voice(engine, "en_US")
# change_voice(engine, "en_US", "VoiceGenderFemale")

rate = engine.getProperty('rate')
# print("rate")
# print(rate)
engine.setProperty('rate', 10)

volume = engine.getProperty('volume')

what_you_typed = input("Type something?\n")

engine.say(f"You typed {what_you_typed}")
engine.runAndWait()

translate_what_you_typed = input("Do you want to hear it in another language?\n")
if (translate_what_you_typed.lower().startswith("y")):
    translated = GoogleTranslator(source='auto', target='pt').translate(what_you_typed)
    print(translated)

    change_voice(engine, "pt_BR")
    engine.say(translated)
    engine.runAndWait()
```

Then, you can test it with `$python test_text.py` and you will see the command similar to this.

```console
Type something?
I like to use Python to learn how to code.

Do you want to hear in with another language?
y
```

You will be able to hear a text translated from what you typed.

If you want to, you can also set the voice to male or female with this.

```py
# VoiceGenderFemale, VoiceGenderMale
change_voice(engine, "en_US", "VoiceGenderFemale")
change_voice(engine, "en_US", "VoiceGenderMale")
```

It doesn't work for all languages options. Therefore, you need to test what is available.

You can also update the target language to translate by editing the target part to what you want.

```py
translated = GoogleTranslator(source='auto', target='pt').translate(what_you_typed)
```

The language options for the **pyttsx3** and the **deep_translator** can be different. You can test some of them for your target language.

If you want to test other audio relevant features with Python, you can refer to [python_audio] repository.

[You can follow me at GitHub.]

[You can contact or hire me at Telegram.]

**Thanks and please share this post with others.**