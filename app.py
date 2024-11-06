# from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
# from flask_cors import CORS
# import pandas as pd
# from model import DonationModel
# import subprocess
# import os
# from flask_mysqldb import MySQL
# import csv
# import traceback 

# app = Flask(__name__)
# CORS(app)

# # MySQL connection configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'  # MySQL username
# app.config['MYSQL_PASSWORD'] = 'Thakshi@2000'  # MySQL password
# app.config['MYSQL_DB'] = 'donor_data_db'

# mysql = MySQL(app)

# # Endpoint to fetch the dataset and return it as a CSV for download
# @app.route('/download_dataset', methods=['GET'])
# def download_dataset():
#     try:
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM donor_data")
#         rows = cur.fetchall()
        
#         # Write dataset to CSV
#         with open('dataset.csv', 'w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([i[0] for i in cur.description])  # Column headers
#             writer.writerows(rows)

#         return send_file('dataset.csv', as_attachment=True)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/run_model', methods=['POST'])

# def run_model():
#     try:
#         steps = int(request.json.get('steps', 10))
#         num_donors = request.json.get('num_donors', 100)
#         num_charities = request.json.get('num_charities', 5)

#         # Initialize the model with donor data
#         model = DonationModel(num_donors, num_charities, pd.read_csv("donor_data_10000.csv"))

#         # Run the model for the number of steps
#         for _ in range(steps):
#             model.step()

#         total_donations = model.total_donation
#         agent_positions = model.get_agent_positions()  # Get agent positions from the model

    


#         return jsonify({
#             'total_donations': total_donations,
#             'agent_positions': agent_positions  # Send agent positions to the frontend
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

     
    
# @app.route('/open_orange', methods=['POST'])
# def open_orange():
#     try:
#         orange_executable_path = r"C:\Users\HP\miniconda3\pkgs\orange3-3.36.2-py39h32e6231_0\Scripts\orange-canvas.exe"
#         orange_shortcut_path = r"C:\Users\HP\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Orange\Orange.lnk"

#         if os.path.exists(orange_shortcut_path):
#             subprocess.Popen(['cmd', '/c', 'start', '', orange_shortcut_path], shell=True)
#         elif os.path.exists(orange_executable_path):
#             subprocess.Popen([orange_executable_path], shell=True)
#         else:
#             raise FileNotFoundError("Orange executable or shortcut not found.")

#         return jsonify({"status": "success", "message": "Orange is opening."})
    
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})

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
    
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import pandas as pd
from model import DonationModel
import subprocess
import os
from flask_mysqldb import MySQL
import csv
import traceback 

app = Flask(__name__)
CORS(app, supports_credentials=True)

# MySQL connection configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # MySQL username
app.config['MYSQL_PASSWORD'] = 'Thakshi@2000'  # MySQL password
app.config['MYSQL_DB'] = 'donor_data_db'

mysql = MySQL(app)

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

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        file = request.files['file']
        df = pd.read_csv(file)

        # Create and run the model using the uploaded donor data
        num_donors = len(df)
        num_charities = 5
        model = DonationModel(num_donors, num_charities, df)

        # Run the model for the number of steps
        for _ in range(10):
            model.step()

        total_donations = model.total_donation
        agent_data = model.get_agent_positions()
        positions = agent_data['positions']
        interactions = agent_data['interactions']
        donation_history = model.donation_history

        return jsonify({
            'total_donations': total_donations,
            'agent_positions': positions,
            'interactions': interactions,
            'donation_history': donation_history
        })

    except Exception as e:
        print('Error in /upload_csv:', str(e))
        traceback.print_exc() 
        return jsonify({'error': str(e)}), 500
    
# @app.route('/login', methods=['POST'])
# def login():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     print(f"Received username: {username}, password: {password}")  # Add this line


#     # Replace the following with actual user authentication logic
#     if username == "testuser" and password == "testpassword": 
#         return jsonify({"username": username})  # Return user data
#     return jsonify({"error": "Invalid credentials"}), 401 
# 

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
        cur.execute("INSERT INTO donations (username, total_donations) VALUES (%s, %s)", (username, total_donations))
        mysql.connection.commit()
        return jsonify({"message": "Donation recorded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, SUM(total_donations) as total FROM donations GROUP BY username ORDER BY total DESC")
        results = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == '__main__':
    app.run(debug=True)




