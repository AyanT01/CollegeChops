from flask import Flask
import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

app = Flask(__name__) 

@app.route("/members")
def members():
    return {"members": ["Member1", "Member2", "Member3"]} 

if __name__ == "__main__":
    app.run(debug=True) 
    