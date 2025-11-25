# File: run.py (root folder)

from app import create_app

from flask_wtf import CSRFProtect

csrf = CSRFProtect()
csrf.init_app(app)  # or csrf = CSRFProtect(app)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
