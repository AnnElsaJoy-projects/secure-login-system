from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session
)

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from email_validator import validate_email, EmailNotValidError

import random
import re



app = Flask(__name__)


# =========================
# CONFIGURATION
# =========================


app.config["SECRET_KEY"] = "secure-login-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)

bcrypt = Bcrypt(app)



login_manager = LoginManager(app)

login_manager.login_view = "login"






# =========================
# DATABASE MODEL
# =========================


class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    username = db.Column(
        db.String(100),
        nullable=False
    )


    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )


    password = db.Column(
        db.String(200),
        nullable=False
    )






@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )







# =========================
# HOME
# =========================


@app.route("/")
def home():

    return render_template(
        "index.html"
    )







# =========================
# REGISTER
# =========================


@app.route(
    "/register",
    methods=["GET","POST"]
)

def register():


    if request.method == "POST":


        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]





        if len(username) < 3:

            flash(
                "Username must contain 3 characters"
            )

            return redirect(
                url_for("register")
            )






        try:

            validate_email(email)


        except EmailNotValidError:


            flash(
                "Invalid email"
            )

            return redirect(
                url_for("register")
            )







        if len(password) < 8:

            flash(
                "Password minimum 8 characters"
            )

            return redirect(
                url_for("register")
            )





        if not re.search("[A-Z]", password):

            flash(
                "Password needs uppercase letter"
            )

            return redirect(
                url_for("register")
            )





        if not re.search("[0-9]", password):

            flash(
                "Password needs number"
            )

            return redirect(
                url_for("register")
            )






        existing_user = User.query.filter_by(
            email=email
        ).first()



        if existing_user:

            flash(
                "Email already registered"
            )

            return redirect(
                url_for("register")
            )







        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")





        user = User(

            username=username,

            email=email,

            password=hashed_password

        )




        db.session.add(user)

        db.session.commit()



        flash(
            "Registration successful"
        )



        return redirect(
            url_for("login")
        )




    return render_template(
        "register.html"
    )









# =========================
# LOGIN
# =========================


@app.route(
    "/login",
    methods=["GET","POST"]
)

def login():


    if request.method == "POST":


        email = request.form["email"]

        password = request.form["password"]




        user = User.query.filter_by(
            email=email
        ).first()





        if user and bcrypt.check_password_hash(

            user.password,

            password

        ):



            otp = random.randint(
                100000,
                999999
            )



            session["otp"] = otp

            session["user_id"] = user.id



            print(
                "Your OTP is:",
                otp
            )



            return redirect(
                url_for("verify_otp")
            )




        else:


            flash(
                "Invalid email or password"
            )




    return render_template(
        "login.html"
    )









# =========================
# OTP VERIFY
# =========================


@app.route(
    "/verify-otp",
    methods=["GET","POST"]
)

def verify_otp():


    if request.method == "POST":


        entered_otp = request.form["otp"]




        saved_otp = session.get(
            "otp"
        )



        user_id = session.get(
            "user_id"
        )





        if saved_otp and int(entered_otp) == saved_otp:



            user = User.query.get(
                user_id
            )



            login_user(
                user
            )



            # remove only otp data

            session.pop(
                "otp",
                None
            )


            session.pop(
                "user_id",
                None
            )



            return redirect(
                url_for("dashboard")
            )




        else:


            flash(
                "Invalid OTP"
            )




    return render_template(
        "verify_otp.html"
    )









# =========================
# DASHBOARD
# =========================


@app.route("/dashboard")

@login_required

def dashboard():


    return render_template(

        "dashboard.html",

        username=current_user.username

    )









# =========================
# PROFILE
# =========================


@app.route("/profile")

@login_required

def profile():


    return render_template(

        "profile.html",

        user=current_user

    )









# =========================
# SECURITY
# =========================


@app.route("/security")

@login_required

def security():


    return render_template(
        "security.html"
    )









# =========================
# LOGOUT
# =========================


@app.route("/logout")

@login_required

def logout():


    logout_user()


    return redirect(
        url_for("login")
    )








# =========================
# CREATE DATABASE
# =========================


with app.app_context():

    db.create_all()






if __name__ == "__main__":

    app.run(
        debug=True
    )