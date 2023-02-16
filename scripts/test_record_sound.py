import pyaudio
import wave
from playsound import playsound

import gtts

import speech_recognition as sr

recognizer = sr.Recognizer()

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1  # 2 failed
fs = 44100  # Record at 44100 samples per second
audio_file = "audio_files/record.wav"

if __name__ == "__main__":
    seconds = input("How many seconds you want to record? (10 seconds by default)\n")
    if seconds == "":
        seconds = 10
    else:
        seconds = int(seconds)

    language = input(
        "Which language you will use? (en-US by default)\n"
    )  # https://cloud.google.com/speech-to-text/docs/languages

    if language == "":
        language = "en-US"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print("Recording")

    stream = p.open(
        format=sample_format,
        channels=channels,
        rate=fs,
        frames_per_buffer=chunk,
        input=True,
    )

    frames = []  # Initialize array to store frames

    # Store data in chunks for 10 seconds
    for i in range(0, int(fs / chunk * (seconds + 1))):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print("End recording")

    # Save the recorded data as a WAV file
    wf = wave.open(audio_file, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b"".join(frames))
    wf.close()

    test_audio_file = input("Do you want to test the audio file?\n")
    if test_audio_file.lower().startswith("y"):
        playsound(audio_file)

    audio_file_to_text = input("Do you want to transcribe the audio file?\n")
    if audio_file_to_text.lower().startswith("y"):
        audio = sr.AudioFile(audio_file)
        with audio as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)

        # recognizer.recognize_google(audio, language="en-US")

        # print(recognizer.recognize_google(audio, language=language))

        transcription = str(recognizer.recognize_google(audio, language=language))

        print("transcription")
        print(transcription)

        save_alt_record_file = input("Do you want to save it to an alt audio file?\n")
        if save_alt_record_file.lower().startswith("y"):
            alt_record_file = "audio_files/alt_record.mp3"
            tts = gtts.gTTS(text=transcription, lang=language, slow=False)
            tts.save(alt_record_file)

            test_alt_record_file = input("Do you want to hear it?\n")
            if test_alt_record_file.lower().startswith("y"):
                playsound(alt_record_file)

# Test sound separately with this
# import speech_recognition as sr
# recognizer = sr.Recognizer()

# audio_file = "audio_files/record.wav"

# text = sr.AudioFile(audio_file)
# with text as source:
#     recognizer.adjust_for_ambient_noise(source)
#     audio = recognizer.record(source)

# recognizer.recognize_google(audio, language="en-US")
