# Refer to this
# https://github.com/Uberi/speech_recognition
# https://github.com/mramshaw/Speech-Recognition
# https://realpython.com/playing-and-recording-sound-python/

# @app.command()
# def requirements():
#     cmd.run(f"pip freeze > requirements.txt", check=True, shell=True)

# @app.command()
# def install():
#     cmd.run(f"pip install -r requirements.txt", check=True, shell=True)

import gtts
from playsound import playsound

import speech_recognition as sr
from speech_recognition import Recognizer, Microphone

import time
import sys

# import os

import pyttsx3


def change_voice(engine, language, gender="VoiceGenderFemale"):
    for voice in engine.getProperty("voices"):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty("voice", voice.id)
            return True

    raise RuntimeError(
        "Language '{}' for gender '{}' not found".format(language, gender)
    )


def recognize_speech_from_mic(recognizer: Recognizer, microphone: Microphone):
    """Transcribe speech recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """

    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {"success": True, "error": None, "transcription": None}

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


if __name__ == "__main__":
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    language = input(
        "Which language you will use? (en-US by default)\n"
    )  # https://cloud.google.com/speech-to-text/docs/languages

    if language == "":
        language = "en_US"

    engine = pyttsx3.init()
    change_voice(engine, language, "VoiceGenderFemale")

    rate = engine.getProperty("rate")
    engine.setProperty("rate", 10)

    print("Say something after 1 second.")

    time.sleep(1)

    what_you_said = recognize_speech_from_mic(recognizer, microphone)

    if what_you_said["error"]:
        print("ERROR: {}".format(what_you_said["error"]))
        sys.exit()

    if not what_you_said["success"]:
        print("I couldn't read that. What did you say?\n")
        sys.exit()

    if what_you_said["transcription"] == None:
        print("Please, say something next time.")
    else:
        # show the user the transcription
        # print("You said: {}".format(what_you_said["transcription"]))
        engine.say("You said {}".format(what_you_said["transcription"]))

        save_audio_file = input("Do you want to save it to an audio file?\n")
        if save_audio_file.lower().startswith("y"):
            tts = gtts.gTTS(what_you_said["transcription"])
            tts.save("audio_files/what_you_said.mp3")

            test_audio_file = input("Do you want to hear it?\n")
            if test_audio_file.lower().startswith("y"):
                audio_file = "audio_files/what_you_said.mp3"

                playsound(audio_file)

                # os.system(f"afplay {audio_file}")
