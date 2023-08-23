# Python Web-App for Quality-Tester
# Created by Jan Macenka (macenka@roi.de) @ 20 Aug 2023

# Library imports
from flask import Flask, render_template, request, jsonify, url_for
import os
import random

# General Parameters
render_context = {
    "COMPANY_NAME": "KOSTAL",
    "MIN_LOAD_TIME_MS": 5000,
    "MAX_RANDOM_LOAD_TIME_MS": 10000,
}

random_check_success_rate = 0.9 # 0.9 means 90% of test will pass if device is connected and 10% will be fails at random
default_user = "pi"

# Functions
def get_foto_files(directory='/media/'):
    """Function that returns a list of all pictures it finds in mounted removable drives.

    Args:
        directory (str, optional): [description]. Defaults to '/media/'.

    Returns:
        list: list of absolute picture paths
    """
    allowed_foto_file_extensions = ['.jpg']  # Add more extensions if needed
    foto_names = []
    for _, _, files in os.walk(directory):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() in allowed_foto_file_extensions:
                foto_names.append(file)
    return foto_names

def check_usb():
    """
    Function that checks that at least one usb device is connected.
    Returns
        bool: True if device is connected, False otherwise
    """
    return len(os.listdir(f'/media/{os.getenv("USER",default_user)}')) != 0

def compare_images():
    """
    Function that checks all found images against a list of allowed images. 
    Returns
        bool: If any of the images is in the allowed list, it returns True, otherwise it returns False.
    """
    list_of_allowed_images = os.listdir('./static/target_pics')
    foto_names = get_foto_files(f'/media/{os.getenv("USER",default_user)}')
    for foto_name in foto_names:
        if foto_name in list_of_allowed_images:
            return (True, foto_name)
    return (False, None)

# Flask instantiation
app = Flask(__name__)

# Routes
@app.route('/')
def home():
    return render_template('index.html', **render_context)

@app.route('/check_software', methods=['POST','GET'])
def check_software():
    if check_usb():
        img_compare_check, foto_name = compare_images()
        if img_compare_check and random.random() < random_check_success_rate:
            return jsonify({"result": "Check Successful", "reason":f"Test completed. Tested product: {foto_name.split('.')[0]}", "picture": f"static/target_pics/{foto_name}"})
        else:
            return jsonify({"result": "Check Failed", "reason": "Measuring results do not match any known product."})
    else:
        return jsonify({"result": "Check Failed", "reason": "Device was not detected"})

# Instantiate
if __name__ == '__main__':
    app.run(debug=True, port=8080)
