import speech_recognition as sr
from speech_recognition import Recognizer, Microphone
import threading


# https://github.com/salesforce/decorator-operations/tree/master/decoratorOperations
def debounce(interval: float):
    """
    Decorator that will debounce a function so that it is called after wait_time seconds
    If it is called multiple times, will wait for the last call to be debounced and run only this one.
    See the test_debounce.py file for examples
    """

    def debounce_decorator(function):
        def debounced_function(*args, **kwargs):
            def call_decorated_function():
                debounced_function._timer = None
                return function(*args, **kwargs)

            if debounced_function._timer is not None:
                debounced_function._timer.cancel()

            debounced_function._timer = threading.Timer(
                interval, call_decorated_function
            )
            debounced_function._timer.start()

        debounced_function._timer = None
        return debounced_function

    return debounce_decorator


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
