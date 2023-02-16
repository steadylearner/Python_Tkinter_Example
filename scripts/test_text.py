# https://github.com/nateshmbhat/pyttsx3
# https://github.com/nidhaloff/deep-translator

# language:

# for voice in engine.getProperty('voices'):
#     print(voice)

# gender    : VoiceGenderFemale, VoiceGenderMale

import pyttsx3
from deep_translator import GoogleTranslator


def change_voice(engine, language, gender="VoiceGenderFemale"):
    for voice in engine.getProperty("voices"):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty("voice", voice.id)
            return True

    raise RuntimeError(
        "Language '{}' for gender '{}' not found".format(language, gender)
    )


engine = pyttsx3.init()
change_voice(engine, "en_US")
# change_voice(engine, "en_US", "VoiceGenderFemale")

rate = engine.getProperty("rate")
# print("rate")
# print(rate)
engine.setProperty("rate", 10)

volume = engine.getProperty("volume")

# print("volume")
# print(volume)
# engine.setProperty('volume', 1.0)

what_you_typed = input("Type something?\n")

engine.say(f"You typed {what_you_typed}")
engine.runAndWait()

translate_what_you_typed = input("Do you want to hear it in another language?\n")
if translate_what_you_typed.lower().startswith("y"):
    translated = GoogleTranslator(source="auto", target="pt").translate(what_you_typed)
    print(translated)

    change_voice(engine, "pt_BR")
    engine.say(translated)
    engine.runAndWait()
