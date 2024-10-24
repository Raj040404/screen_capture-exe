import pyautogui
import time
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import requests
import ollama

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Flag to control the recording process
is_recording = False

def screen_record(duration, interval, output_folder="screenshots"):
    """
    Function to record screenshots at specified intervals.
    """
    global is_recording
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    start_time = time.time()
    counter = 0

    # Continuous check for the recording flag
    while (time.time() - start_time < duration) and is_recording:  
        screenshot = pyautogui.screenshot()
        screenshot.save(os.path.join(output_folder, f"screenshot_{counter}.png"))
        counter += 1
        time.sleep(interval)

        # Check if recording should stop
        if not is_recording:
            break

    print("Screen recording completed.")

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_TOKEN"}

def query(folder="screenshots"):
    """
    Function to extract text from screenshots and query Hugging Face API for image processing.
    """
    text = ""
    text2 = ""

    image_files = [f for f in os.listdir(folder) if f.endswith('.png')]
    
    for image_file in image_files:
        image_path = os.path.join(folder, image_file)
        text2 += extract_text_from_image(image_path)
        with open(image_path, "rb") as f:
            data = f.read()
            response = requests.post(API_URL, headers=headers, data=data)
            text += str(response.json())
    return text, text2

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    """
    image = Image.open(image_path)
    image_np = np.array(image)
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    extracted_text = pytesseract.image_to_string(image_cv)
    return extracted_text

def start_recording(duration, interval):
    """
    Start the screen recording process.
    """
    global is_recording
    is_recording = True  # Set the flag to allow recording
    screen_record(duration, interval)

def stop_recording():
    """
    Stop the screen recording process.
    """
    global is_recording
    is_recording = False  # Set the flag to stop recording

def process_with_ollama(text_data):
    """
    Use ollama model to summarize and extract key points from the given text data.
    """
    desired_model = 'llama3.2:3b'
    ask = "Format the following data and provide summary for and keypoints as well as define the key points of the following: " + str(text_data)
    
    # Assuming ollama.chat returns a dictionary with 'message' containing the 'content'
    response = ollama.chat(model=desired_model, messages=[{
        'role': 'user',
        'content': ask,
    }])

    final = response['message']['content']
    return final

if __name__ == "__main__":
    # Example usage of starting the recording and processing screenshots
    try:
        start_recording(duration=10, interval=2)  # Set appropriate duration and interval
        extracted_text, image_text = query()
        
        # Process extracted text with ollama model
        final_output = process_with_ollama((extracted_text, image_text))
        
        # Save the result to a text file
        with open('text.txt', 'w', encoding='utf-8') as text_file:
            text_file.write(final_output)
        
        # Stop recording
        stop_recording()
        print("Process completed and results saved to text.txt")

    except Exception as e:
        print(f"Error: {e}")
        stop_recording()  # Ensure recording stops on error
