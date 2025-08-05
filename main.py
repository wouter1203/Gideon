import os
import logging
import time
import pyttsx3
from dotenv import load_dotenv
import speech_recognition as sr
from langchain_ollama import ChatOllama, OllamaLLM
# from langchain_openai import ChatOpenAI # if you want to use openai
from langchain_core.messages import HumanMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools.time import get_time 
from tools.duckduckgo import search_duckduckgo
from utils.defaults import get_task_from_prompt
from tools.playwright import search_with_playwright
import re  # Add this import for regular expressions
from utils.state_manager import initialize_db, set_state, get_state, clear_state
from authentication.auth import authenticate  # Import the authentication function

load_dotenv()

MIC_INDEX = 1
TRIGGER_WORD = "Jarvis"
CONVERSATION_TIMEOUT = 30  # seconds of inactivity before exiting conversation mode

logging.basicConfig(level=logging.DEBUG) # logging

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=MIC_INDEX)

# Initialize LLM
llm = ChatOllama(model="mistral", reasoning=False)

# llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, organization=org_id) for openai

# Tool list
tools = [get_time, search_duckduckgo, search_with_playwright]

# Tool-calling prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Jarvis, an intelligent, conversational AI assistant. Your goal is to be helpful, friendly, and informative. You can respond in natural, human-like language and use tools when needed to answer questions more accurately. Always explain your reasoning simply when appropriate, and keep your responses conversational and concise."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Agent + executor
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# TTS setup
def speak_text(text: str):
    try:
        engine = pyttsx3.init()
        
        engine.setProperty('rate', 180)  # Adjust speaking rate
        engine.setProperty('volume', 1.0)  # Adjust volume
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.3)
    except Exception as e:
        logging.error(f"❌ TTS failed: {e}")

# Initialize the database
initialize_db()

# Example usage of state management
def update_state(key, value):
    set_state(key, value)

def fetch_state(key):
    return get_state(key)

# Update the write() function to use the database-backed state
def write():
    # Perform authentication before starting the main loop
    if not authenticate():
        logging.error("❌ Authentication failed. Exiting...")
        speak_text("Authentication failed. Access denied.")
        return  # Exit the function if authentication fails

    logging.info("✅ Authentication successful. Starting wake word detection.")
    speak_text("Authentication successful. Welcome!")

    conversation_mode = fetch_state("conversation_mode") == "True"
    last_interaction_time = float(fetch_state("last_interaction_time") or 0)

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    if not conversation_mode:
                        logging.info("🎤 Listening for wake word...")
                        audio = recognizer.listen(source, timeout=10)
                        transcript = recognizer.recognize_google(audio)
                        logging.info(f"🗣 Heard: {transcript}")

                        if TRIGGER_WORD.lower() in transcript.lower():
                            logging.info(f"🗣 Triggered by: {transcript}")
                            speak_text("Yes sir?")
                            conversation_mode = True
                            update_state("conversation_mode", "True")
                            last_interaction_time = time.time()
                            update_state("last_interaction_time", str(last_interaction_time))
                        else:
                            logging.debug("Wake word not detected, continuing...")
                    else:
                        logging.info("🎤 Listening for next command...")
                        audio = recognizer.listen(source, timeout=10)
                        command = recognizer.recognize_google(audio)
                        logging.info(f"📥 Command: {command}")

                        # Determine the task/tool to activate
                        task = get_task_from_prompt(command)
                        if task:
                            logging.info(f"🔧 Activating tool: {task}")
                            if task == "search_duckduckgo":
                                response = search_duckduckgo(command)
                            elif task == "get_time":
                                response = get_time(command)
                            elif task == "search_with_playwright":
                                # Extract the URL or domain from the command
                                match = re.search(r"(?:visit the website|go to|open)\s+([\w\.-]+\.\w+)", command, re.IGNORECASE)
                                if match:
                                    url = match.group(1)  # Extract the matched URL
                                    if not url.startswith("http"):
                                        url = f"https://{url}"  # Ensure the URL has a valid scheme
                                    response = search_with_playwright(url)
                                    update_state("last_url", url)
                                else:
                                    response = "Sorry, I couldn't find a valid website in your command."
                            else:
                                response = "Sorry, I don't know how to handle that request."
                        else:
                            logging.info("🤖 Sending command to agent...")
                            response = executor.invoke({"input": command})["output"]

                        logging.info(f"✅ Response: {response}")
                        print("Jarvis:", response)
                        speak_text(response)
                        last_interaction_time = time.time()
                        update_state("last_interaction_time", str(last_interaction_time))

                        if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                            logging.info("⌛ Timeout: Returning to wake word mode.")
                            conversation_mode = False
                            update_state("conversation_mode", "False")

                except sr.WaitTimeoutError:
                    logging.warning("⚠️ Timeout waiting for audio.")
                    if conversation_mode and time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        logging.info("⌛ No input in conversation mode. Returning to wake word mode.")
                        conversation_mode = False
                        update_state("conversation_mode", "False")
                except sr.UnknownValueError:
                    logging.warning("⚠️ Could not understand audio.")
                except Exception as e:
                    logging.error(f"❌ Error during recognition or tool call: {e}")
                    time.sleep(1)

    except Exception as e:
        logging.critical(f"❌ Critical error in main loop: {e}")

if __name__ == "__main__":
    write()