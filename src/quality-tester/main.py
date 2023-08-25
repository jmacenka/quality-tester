# Python Web-App for Quality-Tester
# Created by Jan Macenka (macenka@roi.de) @ 20 Aug 2023

# Library imports
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os, json, random, yaml

# General Parameters
default_config = {
    'success_rate': 90, 
    'company_name': 'ROI-EFESO', 
    'min_wait_time': 10000, 
    'max_wait_time': 5000, 
    'default_user': 'pi',
    'logo_name': 'logo.png',
    'password': 'updateplease',
}
target_pics_folder = 'static/target_pics'
config_folder = 'static/configuration'
logo_folder = 'static/img'
config_file_path = os.path.join(config_folder, 'config.yaml')

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
    return len(os.listdir(f'/media/{os.getenv("USER",config.get("default_user", "pi"))}')) != 0

def compare_images():
    """
    Function that checks all found images against a list of allowed images. 
    Returns
        bool: If any of the images is in the allowed list, it returns True, otherwise it returns False.
    """
    list_of_allowed_images = os.listdir('./static/target_pics')
    foto_names = get_foto_files(f'/media/{os.getenv("USER",config.get("default_user", "pi"))}')
    for foto_name in foto_names:
        if foto_name in list_of_allowed_images:
            return (True, foto_name)
    return (False, None)

def load_config_context():
# Load initial values from the configuration file or create it with defaults
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
    else:
        # Create the config file with defaults
        config = default_config
    return config

# Flask instantiation
app = Flask(__name__)
config = load_config_context()

# Ensure the directories exist
os.makedirs(config_folder, exist_ok=True)
os.makedirs(logo_folder, exist_ok=True)

# Routes
@app.route('/')
def home():
    config = load_config_context()
    list_of_allowed_images = os.listdir('./static/target_pics')
    config['allowed_images']=list_of_allowed_images
    return render_template('index.html', **config)

@app.route('/check_software', methods=['POST','GET'])
def check_software():
    if check_usb():
        config = load_config_context()
        img_compare_check, foto_name = compare_images()
        selected_image = request.form.get('selected_image')  # Get the selected image from the form

        # Generate random role to simulate software-check failing randomly
        random_role = random.random()
        success_rate = config['success_rate']/100

        if img_compare_check and random_role <= success_rate and foto_name == selected_image:
            return jsonify({"result": "Check Successful", "reason":f"Test completed. Tested product: {foto_name.split('.')[0]}", "picture": f"static/target_pics/{foto_name}"})
        else:
            return jsonify({"result": "Check Failed", "reason": "Measuring results do not match."})
    else:
        return jsonify({"result": "Check Failed", "reason": f"Device was not detected"})

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    config = load_config_context()

    # Check password
    if request.method == 'POST' and 'password' not in request.form:
        return "Password is required to perform actions."

    if request.method == 'POST' and request.form.get('password') != config['password']:
        return "Incorrect password."

    # Handle parameter updates
    if request.method == 'POST' and 'update-params' in request.form:
        form_success_rate = int(request.form.get('success-rate'))
        form_company_name = request.form.get('company-name')
        form_min_wait_time = int(request.form.get('min-wait-time'))
        form_max_wait_time = int(request.form.get('max-wait-time'))

        # Update values from the form
        config['success_rate'] = form_success_rate
        config['company_name'] = form_company_name
        config['min_wait_time'] = form_min_wait_time
        config['max_wait_time'] = form_max_wait_time

        # Persist updated config to file
        with open(config_file_path, 'w') as config_file:
            yaml.dump(config, config_file)

    # Handle file upload
    if request.method == 'POST' and 'upload-file' in request.form and 'file' in request.files:
        # Check password
        if request.form.get('password') != config['password']:
            return "Incorrect password."

        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(target_pics_folder, filename))

    # Get the list of pictures in the target_pics folder
    pics = os.listdir(target_pics_folder)
    config['pics'] = pics

    return render_template('configure.html', **config)

@app.route('/delete_pic/<filename>', methods=['POST'])
def delete_pic(filename):
    try:
        # Check password
        if request.form.get('password') != config['password']:
            return "Incorrect password."

        os.remove(os.path.join(target_pics_folder, filename))
    except FileNotFoundError:
        pass
    return redirect(url_for('configure'))

@app.route('/logo')
def get_logo():
    logo_files = config['logo_name']
    if logo_files:
        logo_filename = logo_files[0]
        return send_from_directory(logo_folder, logo_filename)
    return "No logo available."

@app.route('/upload_logo', methods=['POST'])
def upload_logo():
    # Check password
    if request.form.get('password') != config['password']:
        return "Incorrect password."

    # Handle file upload
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            logo_files = os.listdir(logo_folder)
            for logo_file in logo_files:
                os.remove(os.path.join(logo_folder, logo_file))

            filename = secure_filename(file.filename)
            file.save(os.path.join(logo_folder, filename))

        # Update and persist updated config to file
        config['logo_name'] = filename
        with open(config_file_path, 'w') as config_file:
            yaml.dump(config, config_file)

    return redirect(url_for('configure'))

# Instantiate
if __name__ == '__main__':
    app.run(debug=True, port=8081)
