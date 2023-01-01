import os
import requests
import time
import threading
import sys
import glob
import subprocess


def download_audio(sentence, i):
    # URL-encode the sentence
    sentence = sentence.replace(" ", "%20")

    # Send a request to the Google Translate TTS API to convert the sentence to speech
    r = requests.get(
        f"https://translate.google.com/translate_tts?ie=UTF-8&q={sentence}&tl=en&total=1&idx=0&textlen=13&client=tw-ob&prev=input"
    )

    # Save the audio file to a file called "sentence{i}.mp3"
    with open(f"sentence{i}.mp3", "wb") as f:
        f.write(r.content)


def play_audio(speed, max):
    # Set the initial sentence index to 1
    i = 1
    print("starting play audio")
    # Start a loop to play the audio files
    print(max + 1)
    while i < max + 1:
        print(i)
        # Check if the audio file for the current sentence exists
        if open("stop.txt").read().strip() == "stopnow":
            with open("stop.txt", "w") as stopFile:
                stopFile.write("")
            with open("running.txt", "w") as runFile:
                runFile.write("")
            print("stop command received")
            raise Exception("Stop command received")

        if os.path.exists(f"sentence{i}.mp3"):
            # Play the audio file
            print(f"mpv --speed={speed} sentence{i}.mp3")
            subprocess.run(
                ["mpv", "--speed=" + str(speed), "sentence" + str(i) + ".mp3"]
            )
            print("finished")
            # Increment the sentence index
            i += 1
        else:
            # Wait for the next audio file to become available
            time.sleep(0.25)


def delete_sentence_files():
    # Find all files in the current directory that match the pattern "sentence*.mp3"
    files = glob.glob("sentence*.mp3")

    # Loop through the files
    for file in files:
        # Delete the file
        os.remove(file)


def split_sentence(sentence):
    # Initialize an empty list for the split sentences
    split_sentences = []

    # Split the sentence into multiple sentences if it is more than 100 characters long
    while len(sentence) > 90:
        # Find the last space before the 100th character
        last_space = sentence[:90].rfind(" ")

        # Split the sentence at the last space
        split_sentences.append(sentence[:last_space])
        sentence = sentence[last_space:]

    # Add the remaining part of the sentence to the list
    split_sentences.append(sentence)

    return split_sentences


def main():
    # Check that a speed parameter was provided
    if len(sys.argv) < 2:
        print("Error: No speed parameter provided")
        sys.exit(1)

    speed = sys.argv[1]

    # Split the text into sentences
    text = os.popen("xsel -o").read()
    print(text)
    sentences = text.split(". ")
    splitSentences = []
    for sentence in sentences:
        splitSentences.extend(split_sentence(sentence))
    for i in range(0, len(splitSentences), 20):
        chunk = splitSentences[i : i + 20]

        for i, sentence in enumerate(chunk):
            t = threading.Thread(target=download_audio, args=(sentence, i + 1))
            t.start()

        # Start a loop to play the audio files
        print("play audio")
        play_audio(speed, len(chunk))
        print("finish played audio")
        delete_sentence_files()


if __name__ == "__main__":
    if open("running.txt").read() == "yes":
        raise Exception("Already running")
    else:
        with open("running.txt", "w") as runFile:
            runFile.write("yes")
    delete_sentence_files()
    main()
    with open("running.txt", "w") as runFile:
        runFile.write("")

split_sentences = []
