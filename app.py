from flask import Flask, render_template
from db.init import init_db_command_init, seed_db_command_init, close_db
import secrets

from routes.web import web_bp
from routes.api import api_bp

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

init_db_command_init(app)
seed_db_command_init(app)

app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", code=404, description=e.description), 404

@app.errorhandler(403)
def access_forbidden(e):
    return render_template("error.html", code=403, description=e.description), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", code=500, description="Wystąpił błąd serwera."), 500

if __name__ == "__main__":
    app.run(debug=True)