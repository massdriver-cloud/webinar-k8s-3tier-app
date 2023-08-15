from flask import Flask, render_template, request
import random
import os
import psycopg2

db_params = {
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD')
}

app = Flask(__name__)

#Create the database
def create_database():
    conn = psycopg2.connect(
        host=db_params['host'],
        port=db_params['port'],
        user=db_params['user'],
        password=db_params['password'])
    
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='gamehistory'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("CREATE DATABASE gamehistory")
    cursor.close()
    conn.close()

# Call the function to create the database
create_database()

# Create the game history table
def create_game_history_table():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS game_history (
        id SERIAL PRIMARY KEY,
        player_choice VARCHAR(10),
        computer_choice VARCHAR(10),
        winner VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()
    

# Call the function to create the table
create_game_history_table()

def get_computer_move():
    options = ["rock", "paper", "scissors"]
    return options[random.randint(0,2)]

def get_winner(player_choice, computer_choice):
    winner = "computer"

    if player_choice == computer_choice:
        winner = "tie"
    if player_choice == "rock" and computer_choice == "scissors":
        winner = "you"
    if player_choice == "scissors" and computer_choice == "paper":
        winner = "you"
    if player_choice == "paper" and computer_choice == "rock":
        winner = "you"

    # Insert game history into the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = "INSERT INTO game_history (player_choice, computer_choice, winner) VALUES (%s, %s, %s)"
    data = (player_choice, computer_choice, winner)
    cursor.execute(query, data)

    conn.commit()
    cursor.close()
    conn.close()

    return winner

@app.route('/', methods=['GET', 'POST'])
def index():
    create_game_history_table()  # Make sure the table exists

    if request.method == 'POST':
        if request.form.get('play_again') == 'Play Again':
            return render_template("index.html")
    return render_template("index.html")

@app.route('/rps', methods=['GET', 'POST'])
def rps():
    if request.method == 'POST':
        choice = request.form.get('choice', 'rock')
    else:
        choice = request.args.get('choice', 'rock')
    player_choice = choice.lower()    
    computer_choice = get_computer_move()
    winner = get_winner(player_choice, computer_choice)
    
    return render_template("rps.html", winner=winner, player_choice=player_choice, computer_choice=computer_choice)

@app.route('/history')
def history():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query = """
    SELECT * FROM game_history ORDER BY created_at DESC;
    """
    cursor.execute(query)
    game_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('history.html', game_history=game_history)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)