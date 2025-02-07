from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="vikas",
    database="flask_data"
)
cursor = db.cursor()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        try:
            cursor.execute("INSERT INTO users_data (name, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()

            session['email'] = email
            return render_template("home.html") 
        except Exception:
            return redirect(url_for("register"))
    else:
        return("Error in registration (email used).") 

    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM users_data WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[2]
            if password == stored_password:
                session['email'] = email  
                return render_template("home.html") 
            else:
                return("Invalid password. Please try again.", "danger")
        else:
            return("Email not found. Please register first.", "danger")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5008)
