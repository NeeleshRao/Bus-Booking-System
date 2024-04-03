from flask import *
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
import os, random, re
from passlib.hash import sha256_crypt
import random
import datetime
from authlib.integrations.flask_client import OAuth
from datetime import timedelta, datetime, date
import smtplib
import jinja2
import pdfkit
from datetime import datetime
import random
from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

################################################################
##################################################################
######################Initializations#############################

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bus_db.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:bablu2002@localhost/bus_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_NAME"] = "login-system"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)
client = MongoClient('localhost', 27017)
db_mongo = client.flask_db
reviews = db_mongo.reviews
db = SQLAlchemy(app)

#######################################################################3
######################################################################
#############ALL MODEL CLASS DEFINITIONS#############################

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, primary_key=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return "<User %r>" % self.email

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(100), nullable=False, unique=True)
    station_location = db.Column(db.String(100), nullable=False)
    station_pincode = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<Station %r>" % self.name

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<Admin %r>" % self.name

class Bus(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    bus_name = db.Column(db.String(100), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    arrival_time = db.Column(db.String(30), nullable=False)
    departure_time = db.Column(db.String(30), nullable=False)
    from_location = db.Column(db.String(200), nullable=False, primary_key=True)
    to_location = db.Column(db.String(11), nullable=False, primary_key=True)

    def __repr__(self):
        return "<Bus %r>" % self.bus_name

class Seats(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_id = db.Column(db.String(100), db.ForeignKey(Bus.id), nullable=False, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    seats_count = db.Column(db.Integer, nullable=False)
    from_location = db.Column(db.String(200), nullable=False, primary_key=True)
    to_location = db.Column(db.String(11), nullable=False, primary_key=True)

    def __repr__(self):
        return "<Seats %r>" % self.bus_id

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_no = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), db.ForeignKey(Users.email), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    seat_no = db.Column(db.String(100), nullable=False)
    bus_id = db.Column(db.String(100), db.ForeignKey(Bus.id), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return "<Book %r>" % self.id

# db.create_all()
# db.drop_all()


@app.route("/")
def home():
    return render_template("Home.html")







#############################################################################
##############################################################################
############# BILL AND USER REVIEWS #########################################

def print_bill(name, email, location, tot_seats, t_number, bus_id, date):
    context = {'name': name, 'email': email, 'location': location, 'tot_seats': tot_seats, 't_number': t_number, 'bus_id': bus_id, 'date': date}
    template_loader = jinja2.FileSystemLoader('./templates')
    template_env = jinja2.Environment(loader=template_loader)

    html_template = 'basic_print.html'
    template = template_env.get_template(html_template)
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='C://Program Files//wkhtmltopdf//bin//wkhtmltopdf.exe')
    output_pdf = 'invoice' + str(random.randint(1000, 100000)) + name +'.pdf'
    pdfkit.from_string(output_text, output_pdf, configuration=config)
    
@app.route("/leave_review", methods=['GET', 'POST'])
def give_review():
    if "user" in session:
        if request.method == "POST":
            review = request.form["user_review"]
            name = request.form["name"]
            email = request.form["email"]
            the_id = Users.query.filter_by(name=name, email=email).first()
            reviews.insert_one({'user_name': name, 'user_review': review})
            flash("Thank you for the review", "message")
            return redirect(url_for('give_review'))
        
        all_reviews = reviews.find()
        return render_template('user_review.html', all_reviews=all_reviews)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))

@app.post("/<id>/delete")
def delete(id):
    reviews.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('userdash'))










#############################################################################
#############################################################################
################### ALL LOGIN ########################

# user login
@app.route("/user_login", methods=["POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        response = Users.query.filter_by(email=email).first()
        if not response:
            flash("Email ID not registered", "error")
            return redirect(url_for("userlog"))
        else:
            checkpass = sha256_crypt.verify(password, response.password)
            if email == response.email and checkpass == True:
                session["user"] = True
                session["user_id"] = response.id
                session["user_name"] = response.name
                session["user_email"] = response.email
                session["user_phone"] = response.phone
                flash("You were successfully logged in", "success")
                return redirect(url_for("userdash"))
            else:
                flash("Invalid Credentials", "error")
                return redirect(url_for("userlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

# main admin login
@app.route("/mainadmin_log", methods=["POST"])
def mainadmin_log():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email == "mainadmin@gmail.com" and password == "entity123":
            session["mainadmin"] = True
            session["mainadmin_name"] = email
            flash("Login Successfull", "success")
            return redirect(url_for("admdash"))
        else:
            flash("Invalid Credentials", "error")
            return redirect(url_for("adminlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

# station admin login
@app.route("/log_admin", methods=["POST"])
def log_admin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        response = Station.query.filter_by(email=email).first()
        if not response:
            flash("Email ID not registered", "error")
            return redirect(url_for("stationlog"))
        else:
            checkpass = sha256_crypt.verify(password, response.password)
            if email == response.email and checkpass == True:
                session["admin"] = True
                session["admin_id"] = response.id
                session["admin_name"] = response.name
                session["admin_phone"] = response.phone
                session["admin_email"] = response.email
                flash("You were successfully logged in", "success")
                return redirect(url_for("stationdash"))
            else:
                flash("Invalid Credentials", "error")
                return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/adminlog")
def adminlog():
    return render_template("adminlog.html")

@app.route("/userlog")
def userlog():
    return render_template("user_log.html")

# logout function for all
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))














#############################################################################
#############################################################################
################### ALL REGISTRATION ########################

@app.route("/admreg")
def admreg():
    return render_template("adminreg.html")

@app.route("/stationreg")
def stationreg():
    return render_template("station_reg.html")

# station admin registeration by main admin
@app.route("/reg_station", methods=["POST"])
def reg_station():
    if request.method == "POST":
        if "mainadmin" in session:
            name_station = request.form["station_name"]
            station_location = request.form["station_location"]
            station_code = request.form["station_code"]
            admin_name = request.form["admin_name"]
            email = request.form["email"]
            phno = request.form["phno"]
            station_check = Station.query.filter_by(station_name=name_station).first()
            if not station_check:
                email_check = Station.query.filter_by(email=email).first()
                if not email_check:
                    phno_check = Station.query.filter_by(phone=phno).first()
                    if not phno_check:
                        hash_pass = sha256_crypt.hash(phno)
                        station = Station(
                            station_name=name_station,
                            station_location=station_location,
                            station_pincode=station_code,
                            name=admin_name,
                            email=email,
                            phone=phno,
                            password=hash_pass,
                        )
                        db.session.add(station)
                        db.session.commit()
                        send_email(
                            email,
                            "Registration Confirmation",
                            "Your station named as "
                            + name_station
                            + " was registered successfully.Use your email and phone number as password for login. Remember to change your password after your first login",
                        )
                        flash("Station registered successfully", "success")
                        return redirect(url_for("admdash"))
                    else:
                        flash("Admin phone number already used", "error")
                        return redirect(url_for("stationreg"))
                else:
                    flash("Admin Mail ID already used", "error")
                    return redirect(url_for("stationreg"))
            else:
                flash("Station name already registered", "error")
                return redirect(url_for("stationreg"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("adminlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/busreg")
def busreg():
    if "admin" in session:
        station_locations = Station.query.distinct(Station.id).all()
        station_access = Station.query.filter_by(email = session["admin_email"]).first()  
        admin_location = station_access.station_location 
        
        
        
        return render_template(
            "Bus_reg.html", location=station_locations, from_location=admin_location
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("adminlog"))
    # return render_template("Bus_reg.html")

# Bus registeration by station admin
@app.route("/bus_submit", methods=["POST"])
def bus_submit():
    if request.method == "POST":
        if "admin" in session:
            bus_id = request.form["bus_id"]
            bus_name = request.form["bus_name"]
            seats = request.form["seats"]
            a_time = request.form["a_time"]
            d_time = request.form["d_time"]
            from_loc = request.form["from_loc"]
            to_loc = request.form["to_loc"]           
            
            id_check = Bus.query.filter_by(id=bus_id, from_location=from_loc, to_location=to_loc).first()
            if from_loc != to_loc:
                if not id_check:                    
                    bus = Bus(
                        id=bus_id,
                        bus_name=bus_name,
                        seats=seats,
                        arrival_time=a_time,
                        departure_time=d_time,
                        from_location=from_loc,
                        to_location=to_loc,
                    )
                    db.session.add(bus)
                    db.session.commit()
                    flash("Bus added successfully", "success")
                    return redirect(url_for("stationdash"))
                    
                else:
                    flash("Bus and Route Entry already done!", "error")
                    return redirect(url_for("busreg"))
            else:
                flash("Start and Destination Same!", "error")
                return redirect(url_for("busreg"))
                
        else:
            flash("Session Expired", "error")
            return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/userreg")
def userreg():
    return render_template("userreg.html")

# user registeration
@app.route("/user_register", methods=["POST"])
def user_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = request.form["password"]
        email_check = Users.query.filter_by(email=email).first()
        if not email_check:
            phone_check = Users.query.filter_by(phone=phone).first()
            if not phone_check:
                flag = 0
                while True:
                    if len(password) < 8:
                        flag = -1
                        break
                    elif not re.search("[a-z]", password):
                        flag = -1
                        break
                    elif not re.search("[A-Z]", password):
                        flag = -1
                        break
                    elif not re.search("[0-9]", password):
                        flag = -1
                        break
                    elif not re.search("[_@$]", password):
                        flag = -1
                        break
                    elif re.search("\\s", password):
                        flag = -1
                        break
                    else:
                        flag = 0
                        break
                if flag == -1:
                    flash("Not a Valid Password", "error")
                    return redirect(url_for("userreg"))
                hash_pass = sha256_crypt.hash(password)
                user = Users(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    password=hash_pass,
                )
                db.session.add(user)
                db.session.commit()
                send_email(
                    email,
                    "Registration Confirmation",
                    "Thank you for registering on our website.Hope you have a good experience",
                )
                flash("Registeration successfully", "success")
                return redirect(url_for("userlog"))
            else:
                flash("Phone Number already registered", "error")
                return redirect(url_for("userreg"))
        else:
            flash("Email ID already registered", "error")
            return redirect(url_for("userreg"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/stationlog")
def stationlog():
    return render_template("Station_log.html")











##########################################################################
##########################################################################
############ UPDATE PROFILES ###########################################

@app.route("/station_profile_update")
def station_profile_update():
    if "admin" in session:
        get_station_data = Station.query.filter_by(id=session["admin_id"]).first()
        return render_template("station_updateform.html", data=get_station_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

# station admin profile update
@app.route("/update_station_profile/<int:id>", methods=["POST"])
def update_station_profile(id):
    if "admin" in session:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]

            phno = request.form["phno"]
            data = Station.query.filter_by(id=id).first()
            email_check = Station.query.filter_by(email=email).first()
            if email_check:
                if email_check.id != id:
                    flash("Email ID is already used by someone else", "error")
                    data = Station.query.filter_by(id=id).first()
                    return render_template("station_updateform.html", data=data)
                elif email_check.id == id:
                    data.email = email
                    data.name = name
                    phno_check = Station.query.filter_by(phone=phno).first()
                    if phno_check:
                        if phno_check.id != id:
                            flash(
                                "Phone number is already used by someone else", "error"
                            )
                            data = Station.query.filter_by(id=id).first()
                            return render_template("station_updateform.html", data=data)
                        elif phno_check.id == id:
                            data.phone = phno
                            db.session.commit()
                            session.clear()
                            flash(
                                "Station admin details updated successfully.Login again to see changes",
                                "success",
                            )
                            return redirect(url_for("stationlog"))
                    else:
                        data.phone = phno
                        db.session.commit()
                        session.clear()
                        flash(
                            "Station admin details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("stationlog"))
            else:
                data.email = email
                data.name = name
                phno_check = Station.query.filter_by(phone=phno).first()
                if phno_check:
                    if phno_check.id != id:
                        flash("Phone number is already used by someone else", "error")
                        data = Station.query.filter_by(id=id).first()
                        return render_template("station_updateform.html", data=data)
                    elif phno_check.id == id:
                        data.phone = phno
                        db.session.commit()
                        session.clear()
                        flash(
                            "Station admin details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("stationlog"))
                else:
                    data.phone = phno
                    db.session.commit()
                    session.clear()
                    flash(
                        "Station admin details updated successfully.Login again to see changes",
                        "success",
                    )
                    return redirect(url_for("stationlog"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

@app.route("/station_profile")
def station_profile():
    if "admin" in session:
        return render_template("station_profile.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))
        
@app.route("/changepass_station")
def changepass_station():
    admin_access = Station.query.filter_by(email=session["admin_email"]).first()
    data = admin_access.station_name    
    return render_template("change_pass_station.html", data = data)

# station admin change password after login
@app.route("/change_station_pass", methods=["POST"])
def change_station_pass():
    if request.method == "POST":
        if "admin" in session:
            name = request.form["name"]
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("changepass_station"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                name_check = Station.query.filter_by(station_name=name).first()
                if name_check:
                    hash_pass = sha256_crypt.hash(pass1)
                    name_check.password = hash_pass
                    db.session.commit()
                    flash("Password changed successfully", "success")
                    return redirect(url_for("stationdash"))
                else:
                    flash("Check your station name and try again", "error")
                    return redirect(url_for("changepass_station"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("changepass_station"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/changepass_user")
def changepass_user():    
    return render_template("change_pass_user.html", data=session["user_email"])

# user change password after login
@app.route("/user_change_pass", methods=["POST"])
def user_change_pass():
    if request.method == "POST":
        if "user" in session:
            email = request.form["email"]
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("changepass_user"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                email_check = Users.query.filter_by(email=email).first()
                if email_check:
                    hash_pass = sha256_crypt.hash(pass1)
                    email_check.password = hash_pass
                    db.session.commit()
                    flash("Password changed successfully", "success")
                    return redirect(url_for("userdash"))
                else:
                    flash("Check your email and try again", "error")
                    return redirect(url_for("changepass_user"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("changepass_user"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("userlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/user_profile")
def user_profile():
    return render_template("user_profile.html")

@app.route("/user_profile_update")
def user_profile_update():
    if "user" in session:
        get_user_data = Users.query.filter_by(id=session["user_id"]).first()
        return render_template("user_profupdate.html", data=get_user_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))

# user profile update
@app.route("/update_user_profile/<int:id>", methods=["POST"])
def update_user_profile(id):
    if "user" in session:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            phno = request.form["phno"]
            address = request.form["address"]
            data = Users.query.filter_by(id=id).first()
            email_check = Users.query.filter_by(email=email).first()
            if email_check:
                if email_check.id != id:
                    flash("Email ID is already used by someone else", "error")
                    data = Users.query.filter_by(id=id).first()
                    return render_template("user_profupdate.html", data=data)
                elif email_check.id == id:
                    data.email = email
                    data.name = name
                    phno_check = Users.query.filter_by(phone=phno).first()
                    if phno_check:
                        if phno_check.id != id:
                            flash(
                                "Phone number is already used by someone else", "error"
                            )
                            data = Users.query.filter_by(id=id).first()
                            return render_template("user_profupdate.html", data=data)
                        elif phno_check.id == id:
                            data.phone = phno
                            data.address = address
                            db.session.commit()
                            session.clear()
                            flash(
                                "User details updated successfully.Login again to see changes",
                                "success",
                            )
                            return redirect(url_for("userlog"))
                    else:
                        data.phone = phno
                        data.address = address
                        db.session.commit()
                        session.clear()
                        flash(
                            "User details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("userlog"))
            else:
                data.email = email
                data.name = name
                phno_check = Users.query.filter_by(phone=phno).first()
                if phno_check:
                    if phno_check.id != id:
                        flash("Phone number is already used by someone else", "error")
                        data = Users.query.filter_by(id=id).first()
                        return render_template("user_profupdate.html", data=data)
                    elif phno_check.id == id:
                        data.phone = phno
                        data.address = address
                        db.session.commit()
                        session.clear()
                        flash(
                            "User details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("userlog"))
                else:
                    data.phone = phno
                    data.address = address
                    db.session.commit()
                    session.clear()
                    flash(
                        "User details updated successfully.Login again to see changes",
                        "success",
                    )
                    return redirect(url_for("userlog"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))









###################################################################################
###################################################################################
##################### DASHBOARDS ##################################################

@app.route("/admdash")
def admdash():
    if "mainadmin" in session:
        buses = Bus.query.count()
        stations = Station.query.count()
        admins = Station.query.count()
        return render_template("Admin_dash.html", data=[buses, stations, admins])
    else:
        flash("Session Expired", "error")
        return redirect(url_for("adminlog"))

@app.route("/userdash")
def userdash():
    if "user" in session:
        buses = Bus.query.count()
        history = Book.query.filter_by(email=session["user_email"]).count()
        return render_template("user_dash.html", data=[buses, history])
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))
  
@app.route("/stationdash")
def stationdash():
    if "admin" in session:
        buses = Bus.query.count()
        users = Users.query.count()
        scheduled_buses = Seats.query.count()
        return render_template(
            "station_dash.html", data=[buses, scheduled_buses, users]
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))













#################################################################################
################################################################################
################ BUS Scheduling by admin all ##################################

@app.route("/buslist")
def buslist():
    if "admin" in session:        
         
        station_access = Station.query.filter_by(email = session["admin_email"]).first()  
        admin_location = station_access.station_location  
        
        data = Bus.query.all() 
        new_data = [] 
        for i in data:
            if i.from_location == admin_location or i.to_location == admin_location:
                new_data.append(i)
                
        return render_template("bus_list.html", data=new_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

@app.route("/add_seat")
def add_seat():
    if "admin" in session:
        data = Bus.query.all()
        station_access = Station.query.filter_by(email = session["admin_email"]).first()  
        admin_location = station_access.station_location 
        
        new_data = [] 
        for i in data:
            if i.from_location == admin_location:
                new_data.append(i)
        
        the_list = []
        newer_data = []
        for i in new_data:
            if i.id not in the_list:
                the_list.append(i.id)
                newer_data.append(i)
        
        return render_template("station_addseat.html", from_location=admin_location, data=newer_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

# station admin schedule bus
@app.route("/schedule_bus", methods=["POST"])
def schedule_bus():
    if "admin" in session:
        if request.method == "POST":
            date_str = request.form["date"]
            bus_id = request.form["bus"]
            from_location = request.form["from_location"]
            to_location = request.form["to_location"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = date.today()
            
            if from_location != to_location:
                
                the_bus = Bus.query.filter_by(id=bus_id, from_location=from_location, to_location=to_location).all()
                print(the_bus)
                if the_bus != []:
                    if date_obj < today:
                        flash(Markup("Selected date is older than today's date"), "error")
                        return redirect(url_for("stationdash"))
                    existing_seats = Seats.query.filter_by(
                        bus_id=bus_id, date=date_str, from_location=from_location, to_location=to_location
                    ).first()
                    if existing_seats:
                        flash("Bus already scheduled for that date and route", "error")
                        return redirect(url_for("stationdash"))
                    bus = Bus.query.filter_by(id=bus_id, from_location=from_location, to_location=to_location).first()
                    seats = Seats(bus_id=bus_id, date=date_str, seats_count=bus.seats, from_location=from_location, to_location=to_location)
                    db.session.add(seats)
                    db.session.commit()
                    flash("Bus scheduled successfully", "success")
                    return redirect(url_for("stationdash"))
                else:
                    flash("Bus does not travel to this destination", "error")
                    return redirect(url_for("stationdash"))
                    
            else:
                flash("Same Source and Destination", "error")
                return redirect(url_for("stationdash"))
                
        else:
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

@app.route("/scheduledbuslist")
def scheduledbuslist():
    if "admin" in session:
        data = Seats.query.all()
        station_access = Station.query.filter_by(email = session["admin_email"]).first()  
        admin_location = station_access.station_location  
        
        new_data = [] 
        for i in data:
            if i.from_location == admin_location or i.to_location == admin_location:
                new_data.append(i)
        return render_template("scheduled_bus_list.html", data=new_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

# list of all buses with reset no.of seats button
@app.route("/reset")
def reset():
    if "admin" in session:
        seats = Seats.query.all()
        return render_template("reset.html", bus=seats)
    else:
        flash("Session expired", "error")
        return redirect(url_for("stationlog"))

# station admin resets no.of seats
@app.route("/reset_seats", methods=["POST"])
def reset_seats():
    if request.method == "POST":
        if "admin" in session:
            id_bus = 0
            date = request.form["date"]
            bus_id = request.form["bus"]
            seats = Seats.query.filter_by(bus_id=bus_id).all()
            for i in seats:
                if i.date == date:
                    id_bus = i.id
                    break
                else:
                    continue
            if id_bus != 0:
                seatss = Seats.query.filter_by(id=id_bus).first()
                seatss.seats_count = 20
                db.session.commit()
                flash("Reset Successfull", "success")
                return redirect(url_for("stationdash"))
            else:
                flash("Selected bus is not sheduled for selected slot", "error")
                return redirect(url_for("reset"))
        else:
            flash("Session expired", "error")
            return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))









#############################################################################
#############################################################################
########### ADMIN HANDLING RESERVATION ######################################

@app.route("/booklist")
def booklist():
    if "admin" in session:
        reservations = Book.query.filter_by(status=0).all()
        return render_template("Booked_list.html", data=reservations)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))
    # reservations = Book.query.filter_by(status=0).all()
    # return render_template("Booked_list.html", data=reservations)

# station admin receives reservation from user
# station admin clicks confirm reservation below function runs
@app.route("/reserve_success/<int:id>")
def reserve_success(id):
    if "admin" in session:
        id_bus = 0
        update_status = Book.query.filter_by(id=id).first()
        bus_id = update_status.bus_id
        tot_seats = update_status.seat_no
        email = update_status.email
        t_number = update_status.ticket_no
        name = update_status.name
        location = update_status.location
        date = update_status.date
        seats = Seats.query.filter_by(bus_id=bus_id).all()
        for i in seats:
            if i.date == date:
                id_bus = i.id
                break
            else:
                continue
        if id_bus != 0:
            seatss = Seats.query.filter_by(id=id_bus).first()
            if seatss.seats_count == 0:
                flash("No Seats available", "error")
                return redirect(url_for("booklist"))
            elif int(tot_seats) > seatss.seats_count:
                flash(f"Only {seatss.seats_count} Seats Available", "error")
                return redirect(url_for("booklist"))
            else:
                updated_seats = seatss.seats_count - int(tot_seats)
                seatss.seats_count = int(updated_seats)
                db.session.commit()
                update_status.status = 1
                db.session.commit()
                body = "Your reservation is successfully. Ticket number is " + str(
                    t_number
                )
                print_bill(name, email, location, tot_seats, t_number, bus_id, date)
                send_email(email, "Reservation Update", body)
                flash("Ticket Booked", "success")
                return redirect(url_for("stationdash"))
        else:
            flash(Markup("Booking is not open for the user's date"), "error")
            return redirect(url_for("booklist"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))

# station admin clicks cancel reservation below function runs
@app.route("/reserve_error/<int:id>")
def reserve_error(id):
    if "admin" in session:
        del_ticket = Book.query.filter_by(id=id).first()
        email = del_ticket.email
        t_number = del_ticket.ticket_no
        db.session.delete(del_ticket)
        db.session.commit()
        body = (
            "Your reservation of ticket number "
            + str(t_number)
            + " is unsuccessfully. It is because no seats were available or no.of seats available are less than the no.of seats required to book your ticket."
        )
        send_email(email, "Reservation Update", body)
        flash("Reservation Cancelled", "error")
        return redirect(url_for("booklist"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("stationlog"))











##################################################################################
###################################################################################
################### USER RESERVATION #############################################

@app.route("/user_reserve")
def user_reserve():
    if "user" in session:
        station_locations = Bus.query.all()
        new_station_locations = []
        the_locations = []
        for i in station_locations:
            if i.to_location not in new_station_locations:
                new_station_locations.append(i.to_location)
                the_locations.append(i)
                
        buses_avialable = Seats.query.all()
        new_bus_id = []
        the_buses_available = [] 
        for i in buses_avialable:
            if i.bus_id not in new_bus_id:
                new_bus_id.append(i.bus_id)
                the_buses_available.append(i)
        
        return render_template(
            "user_reserve.html", location=the_locations, bus=the_buses_available
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))

# user ticket reservation after login
@app.route("/reserve_ticket", methods=["GET", "POST"])
def reserve_ticket():
    if "user" in session:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            location = request.form["location"]
            tot_seats = request.form["seat"]
            date = request.form["travel"]
            bus_id = request.form["bus"]
            t_number = random.randint(999, 999999)
            possible_loc = Bus.query.filter_by(id=bus_id, to_location=location).all()
            print(bus_id, location)
            print(possible_loc, type(possible_loc))
            if possible_loc != []:
                if name and email:
                    users = Book(
                        name=name,
                        email=email,
                        location=location,
                        seat_no=tot_seats,
                        ticket_no=t_number,
                        bus_id=bus_id,
                        date=date,
                        status=0,
                    )
                    db.session.add(users)
                    db.session.commit()
                    body = (
                        "Your reservation request has been sent. Use this reference number "
                        + str(t_number)
                        + " to enquire the status of your reservation"
                    )
                    send_email(email, "Ticket Reservation", body)
                    flash("Request sent for reservation", "success")
                    return redirect(url_for("userdash"))
                else:
                    flash("Name and Email Required", "error")
                    return redirect(url_for("Book_bus"))
            else:
                flash(f"This bus {bus_id} does not travel to your {location}!", "error")
                return redirect(url_for("Book_bus"))
                
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))










###############################################################################
###############################################################################
###################### USER BOOK TICKET #######################################

@app.route("/available_bus")
def available_bus():
    if "user" in session:
        today = datetime.today().strftime("%Y-%m-%d")
        seats = Seats.query.filter(Seats.date >= today).all()
        bus_ids = [seat.bus_id for seat in seats]
        avail = Bus.query.filter(Bus.id.in_(bus_ids)).all()
        print(avail, seats)
        return render_template("availbus_list.html", data=avail, seats=seats)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))

@app.route("/Book_bus")
def Book_bus():
    if "user" in session:
        
        station_locations = Bus.query.all()
        print(type(station_locations[0].id))
        new_station_locations = []
        the_locations = []
        for i in station_locations:
            if i.to_location not in new_station_locations:
                new_station_locations.append(i.to_location)
                the_locations.append(i)
                
        
        buses_avialable = Seats.query.all()  
        new_bus_id = []
        the_buses_available = [] 
        for i in buses_avialable:
            if i.bus_id not in new_bus_id:
                new_bus_id.append(i.bus_id)
                the_buses_available.append(i)   
        
        return render_template(
            "Book_bus.html", location=the_locations, bus=the_buses_available
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))

# user books ticket after login
@app.route("/book_ticket", methods=["POST"])
def book_ticket():
    if request.method == "POST":
        if "user" in session:
            id_bus = 0
            name = request.form["name"]
            email = request.form["email"]
            location = request.form["location"]
            tot_seats = request.form["seat"]
            date = request.form["travel"]
            bus_id = request.form["bus"]
            possible_loc = Bus.query.filter_by(id=bus_id, to_location=location).all()
            print(bus_id, location)
            print(possible_loc, type(possible_loc))
            if possible_loc != []:
                if name and email:
                    seats = Seats.query.filter_by(bus_id=bus_id).all()
                    for i in seats:
                        if i.date == date:
                            id_bus = i.id
                            break
                        else:
                            continue
                    if id_bus != 0:
                        seatss = Seats.query.filter_by(id=id_bus).first()
                        if seatss.seats_count == 0:
                            flash("Sorry No Seats available", "error")
                            return redirect(url_for("Book_bus"))
                        elif int(tot_seats) > seatss.seats_count:
                            flash(f"Only {seatss.seats_count} Seats Available", "error")
                            return redirect(url_for("Book_bus"))
                        else:
                            updated_seats = seatss.seats_count - int(tot_seats)
                            seatss.seats_count = int(updated_seats)
                            t_number = random.randint(999, 999999)
                            db.session.commit()
                            users = Book(
                                name=name,
                                email=email,
                                location=location,
                                seat_no=tot_seats,
                                ticket_no=t_number,
                                bus_id=bus_id,
                                date=date,
                                status=1,
                            )
                            db.session.add(users)
                            db.session.commit()
                            body = (
                                "Your ticket was booked successfully. Your ticket number is: "
                                + str(t_number)
                            )
                            print_bill(name, email, location, tot_seats, t_number, bus_id, date)
                            send_email(email, "Ticket Confirmation", body)
                            flash("Ticket Booked Successfully", "success")
                            return redirect(url_for("userdash"))
                    else:
                        flash("Booking is not open for your date", "error")
                        return redirect(url_for("Book_bus"))
                else:
                    flash("Name and Email Required", "error")
                return redirect(url_for("Book_bus"))
                    
            else:
                flash(f"This bus {bus_id} does not travel to your {location}!", "error")
                return redirect(url_for("Book_bus"))
                
        else:
            flash("Session expired", "error")
            return redirect(url_for("userlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/History")
def History():
    if "user" in session:
        all_booked = Book.query.filter_by(email=session["user_email"]).all()
        allowed = []
        for i in all_booked:
            the_date = i.date
            da = datetime.strptime(the_date, "%Y-%m-%d")
            current = datetime.now()
            if da >= current:
                allowed.append(i)          
        
        # history = Book.query.filter_by(email=session["user_email"]).all()
        return render_template("user_history.html", data=allowed)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))

# cancel ticet after user login
@app.route("/cancel/<int:id>")
def cancel(id):
    if "user" in session:
        id_bus = 0
        check_date = Book.query.filter_by(id=id).first()
        user_date = check_date.date
        seats = check_date.seat_no
        bus = check_date.bus_id
        ticket = check_date.ticket_no
        da = datetime.strptime(user_date, "%Y-%m-%d")
        current = datetime.now()
        tot = da - current
        if da < current:
            if tot.days <= 0:
                flash("Ticket cannot be cancelled before 24hrs", "error")
                return redirect(url_for("History"))
        else:
            change_seats = Seats.query.filter_by(bus_id=bus, date=user_date).first()
            if change_seats is None:
                flash("some error occurred", "error")
                return redirect(url_for("History"))
            new_seats_count = change_seats.seats_count + int(seats)
            change_seats.seats_count = new_seats_count
            db.session.delete(check_date)
            db.session.commit()
            flash("Cancellation successful", "success")
            return redirect(url_for("userdash"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))











#############################################################################
############################################################################
############ MAIN ADMIN FUNCTIONS #########################################

@app.route("/stationlist")
def stationlist():
    if "mainadmin" in session:
        data = Station.query.all()
        return render_template("station_list.html", data=data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("adminlog"))











##########################################################################
############################################################################
############ USER ENQUIRY and other FUNCTIONS ########################################

# ticket number enquiry after login
@app.route("/enquiry", methods=["POST"])
def enquiry():
    if "user" in session:
        if request.method == "POST":
            enquiry = request.form["enquiry"]
            check_ticket_valid = Book.query.filter_by(ticket_no=enquiry).first()
            if not check_ticket_valid:
                flash("Invalid Ticket number", "error")
                return redirect(url_for("userdash"))
            elif check_ticket_valid.status == 0:
                flash("Reservation is in process", "error")
                return redirect(url_for("userdash"))
            else:
                flash("Booking is Done", "success")
                return redirect(url_for("userdash"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("userlog"))








###############################################################################
###############################################################################
###############################################################################
###########################################USELESS GOOGLE######################

@app.route("/station_forpass_form")
def station_forpass_form():
    return render_template("station_forpass_form.html")

@app.route("/user_forpass_form")
def user_forpass_form():
    return render_template("user_forpass_form.html")

# user change password after otp verification
@app.route("/change_user_pass", methods=["POST"])
def change_user_pass():
    if request.method == "POST":
        if "user" in session:
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("user_forpass_form"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data = Users.query.filter_by(email=session["email"]).first()
                data.password = hash_pass
                db.session.commit()
                session.pop("user", None)
                session.pop("email", None)
                flash("Password changed successfully", "success")
                return redirect(url_for("userlog"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("user_forpass_form"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("userlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/user_otp")
def user_otp():
    return render_template("user_otp.html")

# user otp verification for forgot password
@app.route("/user_verify", methods=["POST"])
def user_verify():
    if request.method == "POST":
        if "user" in session:
            user_otp = request.form["user_otp"]
            if session["otp"] == int(user_otp):
                return redirect(url_for("user_forpass_form"))
            else:
                flash("Wrong OTP. Please try again", "error")
                return redirect(url_for("user_otp"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("userlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

# station admin otp verification to recover password
@app.route("/admin_verify", methods=["POST"])
def admin_verify():
    if request.method == "POST":
        if "station" in session:
            admin_otp = request.form["admin_otp"]
            if session["otp"] == int(admin_otp):
                return redirect(url_for("station_forpass_form"))
            else:
                flash("Wrong OTP. Please try again", "error")
                return redirect(url_for("station_otp"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

# register with google
@app.route("/authorize")
def authorize():
    google = oauth.create_client("google")  # create the google oauth client
    token = (
        google.authorize_access_token()
    )  # Access token from google (needed to get user info)
    resp = google.get("userinfo")  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    hash_pass = sha256_crypt.hash(user_info["email"])
    response = Users.query.filter_by(email=user_info["email"]).first()
    if response:
        session["user"] = True
        session["user_id"] = response.id
        session["user_name"] = response.name
        session["user_email"] = response.email
        session["user_phone"] = response.phone
        flash("You were successfully logged in", "success")
        return redirect(url_for("userdash"))
    else:
        phone = random.randint(9999999, 9999999999)
        user = Users(
            name=user_info["name"],
            email=user_info["email"],
            phone=phone,
            address="Enter your address here",
            password=hash_pass,
        )
        db.session.add(user)
        db.session.commit()
        respons = Users.query.filter_by(email=user.email).first()
        session["user"] = True
        session["user_id"] = respons.id
        session["user_name"] = respons.name
        session["user_email"] = respons.email
        session["user_phone"] = respons.phone
        session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
        flash("Update your phone and address", "success")
        return redirect(url_for("user_profile_update"))

# login with google
@app.route("/login_google")
def login_google():
    google = oauth.create_client("google")  # create the google oauth client
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(redirect_uri)

# user forgot password
@app.route("/user_send_otp", methods=["POST"])
def user_send_otp():
    if request.method == "POST":
        email = request.form["email"]
        email_check = Users.query.filter_by(email=email).first()
        if email_check:
            session["user"] = True
            session["email"] = email_check.email
            otp = random.randint(000000, 999999)
            session["otp"] = otp
            body = (
                "Dear "
                + email_check.name
                + ", your OTP for Password Recovery is: "
                + str(otp)
            )
            send_email(email, "OTP for Password change", body)
            flash("OTP sent", "success")
            return redirect(url_for("user_otp"))
        else:
            flash(
                "Email ID not registered. Please check your email id or create a new account",
                "error",
            )
            return redirect(url_for("userlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

# station admin forgot password
@app.route("/admin_send_otp", methods=["POST"])
def admin_send_otp():
    if request.method == "POST":
        email = request.form["email"]
        email_check = Station.query.filter_by(email=email).first()
        if email_check:
            session["station"] = True
            session["email"] = email_check.email
            otp = random.randint(000000, 999999)
            session["otp"] = otp
            body = (
                "Dear "
                + str(email_check.name)
                + ", your verification code is: "
                + str(otp)
            )
            send_email(email, "OTP for Station Admin Password Recovery", body)
            flash("OTP sent", "success")
            return redirect(url_for("station_otp"))
        else:
            flash("Email ID not registered. Please contact Main Admin", "error")
            return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))

@app.route("/station_otp")
def station_otp():
    return render_template("station_otp.html")

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id="YOUR CLIENT ID",
    client_secret="YOUR CLIENT SECRET",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    # This is only needed if using openId to fetch user info
    client_kwargs={
        "scope": "openid email profile",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
    },
)

def send_email(recipient, subject, body):
    FROM = "YOUR GMAIL ID"
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body + "\n\nThanks & Regards,\nTeam Bookezy"

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (
        FROM,
        ", ".join(TO),
        SUBJECT,
        TEXT,
    )
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login("YOUR GMAIL ID", "YOUR APP PASSWORD")
        server.sendmail(FROM, TO, message)
        server.close()
    except:
        flash("Check your internet connection", "error")
        return redirect(url_for("home"))

@app.route("/user_forpass")
def user_forpass():
    return render_template("user_forpass.html")

@app.route("/station_forpass")
def station_forpass():
    return render_template("station_forpass.html")

# station admin setting up new password
@app.route("/change_admin_pass", methods=["POST"])
def change_admin_pass():
    if request.method == "POST":
        if "station" in session:
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("station_forpass_form"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data = Station.query.filter_by(email=session["email"]).first()
                data.password = hash_pass
                db.session.commit()
                session.pop("station", None)
                session.pop("email", None)
                flash("Password changed successfully", "success")
                return redirect(url_for("stationlog"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("station_forpass_form"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("stationlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=9876)
