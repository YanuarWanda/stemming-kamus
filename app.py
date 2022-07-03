from website import create_app
from flaskext.mysql import MySQL

app = create_app()
mysql = MySQL(app)
if __name__ == "__main__":
    app.run(debug = True)