from flask import Flask, render_template,request,session,redirect,url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="vikas",
    database="user_data"
)
cursor = db.cursor()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Insert User Data into Database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        db.commit()
        return "Registration Successful! <a href='/'>Go to Login</a>"
    
    @app.route("/login", methods=['GET','POST'])
    def login():
     if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check User in Database
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session["user"] = username
            return f"Welcome {username}! <a href='/logout'>Logout</a>"
        else:
            return "Invalid Credentials! <a href='/'>Try Again</a>"

    # Logout Route
    @app.route("/logout")
    def logout():
     session.pop("user", None)
     return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5004)
