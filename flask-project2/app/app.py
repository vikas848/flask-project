from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector
import os
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load API key from env variable (recommended)
myapi_key = os.getenv("OPENAI_API_KEY")
gptclient = OpenAI(api_key=myapi_key)

# Database connection
# db = mysql.connector.connect(
#     host="172.18.0.2",
#     user="root",
#     password="vikas",
#     database="flask_data",
#     autocommit=True
# )
db = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "flaskapp"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", "vikas"),
    database=os.environ.get("MYSQL_DATABASE", "flask_data"),
    autocommit=True
)
cursor = db.cursor()

@app.route("/")
def log():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM users_data WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[2]
            if check_password_hash(stored_password, password):
                session['email'] = email  # Store actual email
                return redirect(url_for('home'))
            else:
                flash("Invalid password. Please try again.", "danger")
        else:
            flash("Email not found. Please register first.", "danger")

    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users_data (name, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            db.commit()
            session['email'] = email
            flash("Registration successful!", "success")
            return redirect(url_for('home'))
        except mysql.connector.IntegrityError:
            flash("Email already exists. Try another!", "danger")

    return render_template("index.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('email'):
        return redirect(url_for('log'))

    my_output = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')

        if user_input:
            try:
                completion = gptclient.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Your only task is to correct grammar and spelling mistakes. Do not provide any other information."},
                        {"role": "user", "content": user_input}
                    ]
                )
                my_output = completion.choices[0].message.content
            except Exception as e:
                my_output = f"An error occurred: {str(e)}"
        else:
            my_output = "Please enter some text."

        return render_template('home.html', user_input=my_output)

    return render_template('home.html', user_input=my_output)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('log'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)