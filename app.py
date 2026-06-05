from flask import Flask
from db.init import init_db_command_init, seed_db_comand_init, close_db

app = Flask(__name__)
app.teardown_appcontext(close_db)

init_db_command_init(app)
seed_db_comand_init(app)

if __name__ == "__main__":
    app.run(debug=True)