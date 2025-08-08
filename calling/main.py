from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import pyttsx3
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
import speech_recognition as sr
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize Ollama LLM
llm = OllamaLLM(model="mistral")  # Ensure the model is accessible
prompt_template = PromptTemplate(
    input_variables=["user_input"],
    template="Your name is Gideon, you are a personal assistant. Respond to the following: {user_input}"
)
llm_chain = RunnableSequence(prompt_template, llm)


def convert_audio_to_text(audio_file_path):
    """
    Converts an audio file to text using the SpeechRecognition library.
    :param audio_file_path: Path to the audio file.
    :return: Transcribed text or None if transcription fails.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)  # Read the audio file
            transcript = recognizer.recognize_google(audio_data)  # Use Google Web Speech API
            return transcript
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Speech Recognition service; {e}")
        return None

def process_recording_async(recording_url):
    try:
        max_retries = 5  # Number of retries
        delay = 2  # Delay in seconds before the first attempt

        print(f"Waiting {delay} seconds before the first attempt to download recording...")
        time.sleep(delay)  # Delay before the first attempt

        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1} to download recording...")
            response = requests.get(
                recording_url,
                auth=HTTPBasicAuth("ACfae0b792cebbdf9b92c0b2dc724abe89", "8dbff6a472cd2f7612f138585ed0aaed")
            )
            if response.status_code == 200:
                # Save the recording locally
                audio_file_path = "user_recording.wav"
                with open(audio_file_path, "wb") as f:
                    f.write(response.content)
                print("Recording downloaded successfully.")

                # Convert the audio file to text using a speech-to-text service
                transcript = convert_audio_to_text(audio_file_path)
                print(f"Transcript: {transcript}")

                # Invoke the LLM
                answer = llm_chain.invoke({"user_input": transcript})
                print(f"LLM Response: {answer}")
                return  # Exit after successful processing

            print(f"Failed to download recording. Status code: {response.status_code}")
            time.sleep(delay)  # Wait before retrying

        print("Max retries reached. Could not download recording.")
    except Exception as e:
        print(f"Error processing recording: {e}")

@app.route("/voice", methods=["POST"])
def voice():
    # Check if this is the first interaction
    is_initial = request.args.get("initial", "true") == "true"

    # Twilio VoiceResponse
    resp = VoiceResponse()

    if is_initial:
        # Generate the opening message
        opening_message = "Hello! Welcome to your AI assistant. How can I help you today?"
        resp.say(opening_message)
    else:
        # Continue the conversation
        resp.say("How can I assist you further?")

    # Record the user's response
    resp.record(
        timeout=5,
        transcribe=True,
        max_length=10,
        action="/process",
        transcribe_callback="/process"
    )

    return Response(str(resp), mimetype="text/xml")


@app.route("/process", methods=["POST"])
def process():
    recording_url = request.form.get("RecordingUrl")
    transcript = None

    if recording_url:
        print(f"Recording URL: {recording_url}")
        try:
            # Wait for Twilio to process the recording
            time.sleep(2)  # Initial delay before the first attempt

            # Download the recording
            response = requests.get(
                recording_url,
                auth=HTTPBasicAuth("ACfae0b792cebbdf9b92c0b2dc724abe89", "8dbff6a472cd2f7612f138585ed0aaed")
            )
            if response.status_code == 200:
                # Save the recording locally
                audio_file_path = "user_recording.wav"
                with open(audio_file_path, "wb") as f:
                    f.write(response.content)
                print("Recording downloaded successfully.")

                # Convert the audio file to text
                transcript = convert_audio_to_text(audio_file_path)
                print(f"Transcript: {transcript}")
            else:
                print(f"Failed to download recording. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading recording: {e}")

    # Handle cases where transcript is unavailable
    if not transcript:
        response = VoiceResponse()
        response.say("Sorry, I couldn't understand your response. Please try again.")
        response.redirect("/voice")
        return Response(str(response), mimetype="text/xml")

    # Process the transcript with LLM
    try:
        answer = llm_chain.invoke({"user_input": transcript})
        print(f"LLM Response: {answer}")
    except Exception as e:
        print(f"Error generating response: {e}")
        answer = "Sorry, I couldn't process your request."

    # Respond to the user with the generated answer
    response = VoiceResponse()
    response.say(answer, voice='alice')
    response.redirect("/voice")  # Redirect back to /voice to restart the listening process
    return Response(str(response), mimetype="text/xml")

@app.route("/handle-keypress", methods=["POST"])
def handle_keypress():
    print("Request data:", request.form)  # Log the incoming request data
    digit_pressed = request.form.get("Digits")
    print(f"Digit pressed: {digit_pressed}")

    response = VoiceResponse()

    if digit_pressed == "1":
        response.say("You pressed 1. Thank you!")
    else:
        response.say("Invalid input. Please try again.")

    return Response(str(response), mimetype="text/xml")

def generate_opening_message():
    # Get the current hour
    current_hour = datetime.now().hour

    # Determine the greeting based on the time of day
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Generate the opening message
    opening_message = f"{greeting}, my name is Gideon. How can I help you today?"
    audio_file = "opening_message.mp3"

    # Use pyttsx3 to save the generated speech to an audio file
    engine = pyttsx3.init()
    engine.save_to_file(opening_message, audio_file)
    engine.runAndWait()

    return audio_file

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
