from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import pandas as pd
from model import DonationModel
import subprocess
import os
from flask_mysqldb import MySQL
import csv
import traceback 
from dotenv import load_dotenv
from flask import session
from flask import request
from flask_session import Session

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Replace with a strong secret key


CORS(app, supports_credentials=True)

# Set a maximum content length for file uploads (e.g., 100MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# MySQL connection configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')  # MySQL username
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')  # MySQL password
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

# Configure session to use filesystem (or any other backend like Redis for production)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Endpoint to fetch the dataset and return it as a CSV for download
@app.route('/download_dataset', methods=['GET'])
def download_dataset():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM donor_data")
        rows = cur.fetchall()
        
        # Write dataset to CSV
        with open('dataset.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([i[0] for i in cur.description])  # Column headers
            writer.writerows(rows)

        return send_file('dataset.csv', as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_model', methods=['POST'])

def run_model():
    try:
        steps = int(request.json.get('steps', 10))
        num_donors = request.json.get('num_donors', 100)
        num_charities = request.json.get('num_charities', 5)

        # Initialize the model with donor data
        model = DonationModel(num_donors, num_charities, pd.read_csv("donor_data_10000.csv"))

        # Run the model for the number of steps
        for _ in range(steps):
            model.step()

        total_donations = model.total_donation
        agent_positions = model.get_agent_positions()  # Get agent positions from the model

    


        return jsonify({
            'total_donations': total_donations,
            'agent_positions': agent_positions  # Send agent positions to the frontend
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

     
    
@app.route('/open_orange', methods=['POST'])
def open_orange():
    try:
        orange_executable_path = r"C:\Users\HP\miniconda3\pkgs\orange3-3.36.2-py39h32e6231_0\Scripts\orange-canvas.exe"
        orange_shortcut_path = r"C:\Users\HP\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Orange\Orange.lnk"

        if os.path.exists(orange_shortcut_path):
            subprocess.Popen(['cmd', '/c', 'start', '', orange_shortcut_path], shell=True)
        elif os.path.exists(orange_executable_path):
            subprocess.Popen([orange_executable_path], shell=True)
        else:
            raise FileNotFoundError("Orange executable or shortcut not found.")

        return jsonify({"status": "success", "message": "Orange is opening."})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# @app.route('/upload_csv', methods=['POST'])
# def upload_csv():
#     try:
#         file = request.files['file']
#         df = pd.read_csv(file)

#         # Create and run the model using the uploaded donor data
#         num_donors = len(df)
#         num_charities = 5
#         model = DonationModel(num_donors, num_charities, df)

#         # Run the model for the number of steps
#         for _ in range(10):
#             model.step()

#         total_donations = model.total_donation
#         agent_data = model.get_agent_positions()
#         positions = agent_data['positions']
#         interactions = agent_data['interactions']
#         donation_history = model.donation_history

#         return jsonify({
#             'total_donations': total_donations,
#             'agent_positions': positions,
#             'interactions': interactions,
#             'donation_history': donation_history
#         })

#     except Exception as e:
#         print('Error in /upload_csv:', str(e))
#         traceback.print_exc() 
#         return jsonify({'error': str(e)}), 500
    

# @app.route('/upload_csv', methods=['POST'])
# def upload_csv():
#     try:
#         # Handle the CSV file upload (this is for simulation)
#         file = request.files.get('file')  # Donor CSV file for simulation
#         model_file = request.files.get('model_file')  # Model file (not used in simulation)
#         analyzed_donations = request.form.get('analyzed_donations')  # Analyzed donation amount
        
#         # Check if the CSV file and analyzed donations field are provided
#         if not file or not analyzed_donations:
#             return jsonify({'error': 'Missing required fields (CSV file and analyzed_donations)'}), 400

#         # Handle Model File Upload (This can be any file type)
#         if model_file:
#             model_filename = model_file.filename
#             model_file_path = os.path.join('models', model_filename)  # Save model file in 'models' directory
#             os.makedirs(os.path.dirname(model_file_path), exist_ok=True)
#             model_file.save(model_file_path)

#         # Read the CSV file for donor data (this will be used for simulation)
#         df = pd.read_csv(file)

#         # Create and run the model using the uploaded donor data (simulation)
#         num_donors = len(df)
#         num_charities = 5
#         model = DonationModel(num_donors, num_charities, df)

#         # Run the model for the number of steps (simulation process)
#         for _ in range(10):
#             model.step()

#         total_donations = model.total_donation  # Calculated donation total from the simulation
#         agent_data = model.get_agent_positions()
#         positions = agent_data['positions']
#         interactions = agent_data['interactions']
#         donation_history = model.donation_history

#         # Insert simulated total donation amount, model file, and analyzed donation into the database
#         cur = mysql.connection.cursor()
#         cur.execute("""
#             INSERT INTO donations (username, total_donations, timestamp, model_file, analyzed_donations) 
#             VALUES (%s, %s, NOW(), %s, %s)
#         """, (session.get('username', 'admin'), total_donations, model_file_path, analyzed_donations))
#         mysql.connection.commit()

#         return jsonify({
#             'total_donations': total_donations,
#             'agent_positions': positions,
#             'interactions': interactions,
#             'donation_history': donation_history
#         })

#     except Exception as e:
#         # Add better error logging
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        # Handle the CSV file upload (this is for simulation)
        file = request.files.get('file')  # Donor CSV file for simulation
        model_file = request.files.get('model_file')  # Model file (not used in simulation)
        analyzed_donations = request.form.get('analyzed_donations')  # Analyzed donation amount
        
        # Check if the CSV file and analyzed donations field are provided
        if not file or not analyzed_donations:
            return jsonify({'error': 'Missing required fields (CSV file and analyzed_donations)'}), 400

        # Handle Model File Upload (This can be any file type)
        if model_file:
            model_filename = model_file.filename
            model_file_path = os.path.join('models', model_filename)  # Save model file in 'models' directory
            os.makedirs(os.path.dirname(model_file_path), exist_ok=True)
            model_file.save(model_file_path)  # Save the file to the server

        # Read the CSV file for donor data (this will be used for simulation)
        df = pd.read_csv(file)

        # Create and run the model using the uploaded donor data (simulation)
        num_donors = len(df)
        num_charities = 5
        model = DonationModel(num_donors, num_charities, df)

        # Run the model for the number of steps (simulation process)
        for _ in range(10):
            model.step()

        total_donations = model.total_donation  # Calculated donation total from the simulation
        agent_data = model.get_agent_positions()
        positions = agent_data['positions']
        interactions = agent_data['interactions']
        donation_history = model.donation_history

        # Insert simulated total donation amount, model file path, and analyzed donation into the database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO donations (username, total_donations, timestamp, model_file, analyzed_donations) 
            VALUES (%s, %s, NOW(), %s, %s)
        """, (session.get('username', 'admin'), total_donations, model_file_path, analyzed_donations))
        mysql.connection.commit()

        return jsonify({
            'total_donations': total_donations,
            'agent_positions': positions,
            'interactions': interactions,
            'donation_history': donation_history
        })

    except Exception as e:
        # Add better error logging
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# Endpoint to handle model file downloads
@app.route('/download_model/<int:model_id>', methods=['GET'])
def download_model(model_id):
    try:
        cur = mysql.connection.cursor()
        # Fetch the model file path based on the provided ID
        cur.execute("SELECT model_file FROM donations WHERE id = %s", (model_id,))
        model_file_path = cur.fetchone()

        if model_file_path and os.path.exists(model_file_path[0]):
            return send_file(model_file_path[0], as_attachment=True)

        return jsonify({'error': 'Model file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        cur = mysql.connection.cursor()
        # Query to check for the user in the database
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()  # Fetch one record
        
        if user:
            session['username'] = username
            return jsonify({"username": username})  # Successful login
        else:
            return jsonify({"error": "Invalid credentials"}), 401  # Failed login
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle database errors
    

@app.route('/submit_donation', methods=['POST'])
def submit_donation():
    username = request.json.get('username')
    total_donations = request.json.get('total_donations')

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO donations (username, total_donations, timestamp) 
            VALUES (%s, %s, NOW())
        """, (username, total_donations))
        mysql.connection.commit()

        # Fetch the last inserted ID and store it in the session
        cur.execute("SELECT LAST_INSERT_ID()")
        last_id = cur.fetchone()[0]
        print(f"Last Inserted ID: {last_id}")  # Debugging

        session['last_inserted_id'] = last_id

        return jsonify({"message": "Donation recorded successfully", "last_id": last_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route('/leaderboard', methods=['GET'])
# def leaderboard():
#     try:
#         cur = mysql.connection.cursor()
#         # Fetch username, total_donations, and timestamp
#         cur.execute("""
#             SELECT username, total_donations, timestamp
#             FROM donations
#             ORDER BY timestamp DESC
#         """)
#         results = cur.fetchall()

#         # Format the data for the response
#         leaderboard_data = []
#         for row in results:
#             leaderboard_data.append({
#                 "username": row[0],
#                 "total_donations": row[1],
#                 "timestamp": row[2]
#             })

#         return jsonify(leaderboard_data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        cur = mysql.connection.cursor()
        # Fetch username, total_donations, analyzed_donations, model_file, and other details
        cur.execute("""
            SELECT username, total_donations, analyzed_donations, model_file, timestamp, id
            FROM donations
            ORDER BY timestamp DESC
        """)
        results = cur.fetchall()

        # Format the data for the response
        leaderboard_data = []
        for row in results:
            leaderboard_data.append({
                "username": row[0],
                "total_donations": row[1],
                "analyzed_donations": row[2] if row[2] is not None else 'N/A',
                "model_file": row[3] if row[3] is not None else 'N/A',  # Return model file path (not binary data)
                "timestamp": row[4],
                "id": row[5]  # Include the ID for download link
            })

        return jsonify(leaderboard_data), 200  # Return the leaderboard data in JSON format

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error in case of exception


@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        cur = mysql.connection.cursor()
        # Check if the username already exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return jsonify({"success": False, "message": "Username already exists."}), 400

        # Insert the new user into the users table
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
if __name__ == '__main__':
    app.run(debug=True)
