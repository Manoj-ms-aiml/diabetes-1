# app.py
from flask import Flask, render_template, request, redirect, session, url_for, flash
import numpy as np
import joblib
import webbrowser
from werkzeug.serving import is_running_from_reloader
import mysql.connector
import pandas as pd
import json
from datetime import datetime

app=Flask(__name__)
app.secret_key = "secret123"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route('/team')
def team():
    return render_template("team.html")

@app.route('/info')
def info():
    return render_template("info.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

# ------------------- Database Connection -------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
        port=3306,
        user="root",
        password="root",
        database="medicaldatabase",
         use_pure=True
        )
        return conn
    except mysql.connector.Error as e:
        print("❌ DB Connection Error:", e)
        return None


# ------------------- User Login Helpers -------------------
def check_tblusers_login(userid, password, role):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)  # <-- dictionary cursor
    cursor.execute(
        "SELECT * FROM tblusers WHERE userid=%s AND password=%s AND usertype=%s",
        (userid, password, role)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def check_patient_login(patientid, password):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM tblpatients WHERE patientid=%s AND password=%s",
        (patientid, password)
    )
    patient = cursor.fetchone()
    conn.close()
    return patient


# ------------------- Login Routes -------------------
@app.route("/adminlogin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        userid = request.form["userid"]
        password = request.form["password"]

        user = check_tblusers_login(userid, password, "admin")
        if user:
            session.update({"userid": user["userid"], "username": user["name"], "role": "admin"})
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_home"))
        else:
            flash("Invalid Admin credentials!", "danger")
    return render_template("adminlogin.html")

@app.route("/receptionistlogin", methods=["GET", "POST"])
def receptionist_login():
    if request.method == "POST":
        userid = request.form["userid"]
        password = request.form["password"]

        user = check_tblusers_login(userid, password, "receptionist")
        if user:
            session.update({"userid": user["userid"], "username": user["name"], "role": "receptionist"})
            flash("Receptionist login successful!", "success")
            return redirect(url_for("receptionist_home"))
        else:
            flash("Invalid Receptionist credentials!", "danger")
    return render_template("receptionistlogin.html")

@app.route("/doctorlogin", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        userid = request.form["userid"]
        password = request.form["password"]

        user = check_tblusers_login(userid, password, "doctor")
        if user:
            session.update({"userid": user["userid"], "username": user["name"], "role": "doctor"})
            flash("Doctor login successful!", "success")
            return redirect(url_for("doctor_home"))
        else:
            flash("Invalid Doctor credentials!", "danger")
    return render_template("doctorlogin.html")

@app.route("/patientlogin", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        patientid = request.form["patientid"]
        password = request.form["password"]

        patient = check_patient_login(patientid, password)
        if patient:
            session.update({"userid": patient["patientid"], "username": patient["name"], "role": "patient"})
            flash("Patient login successful!", "success")
            return redirect(url_for("patient_home"))
        else:
            flash("Invalid Patient credentials!", "danger")
    return render_template("patientlogin.html")


# ------------------- Home/Dashboard Routes -------------------
@app.route("/adminhome")
def admin_home():
    if session.get("role") == "admin":
        return render_template("adminhome.html", username=session["username"])
    return redirect(url_for("adminlogin"))

@app.route("/receptionisthome")
def receptionist_home():
    if session.get("role") == "receptionist":
        return render_template("receptionisthome.html", username=session["username"])
    return redirect(url_for("receptionist_login"))

@app.route("/doctorhome")
def doctor_home():
    if session.get("role") == "doctor":
        return render_template("doctorhome.html", username=session["username"])
    return redirect(url_for("doctor_login"))

@app.route("/patienthome")
def patient_home():
    if session.get("role") == "patient":
        return render_template("patient_home.html", username=session["username"])
    return redirect(url_for("patient_login"))

# ------------------- USER MANAGEMENT -------------------

# Show all users
@app.route("/users")
def users_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblusers where usertype!=%s", ('admin',))
    users = cursor.fetchall()
    conn.close()
    return render_template("users_list.html", users=users)


# Add User
@app.route("/adduser", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        userid = request.form["userid"]
        password = request.form["password"]
        name = request.form["name"]
        mobile = request.form["mobile"]
        emailid = request.form["emailid"]
        usertype = request.form["usertype"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tblusers (userid, password, name, mobile, emailid, usertype)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (userid, password, name, mobile, emailid, usertype))
        conn.commit()
        conn.close()

        flash("✅ User added successfully!", "success")
        return redirect(url_for("users_list"))

    return render_template("add_user.html")


# Edit User (load form with existing data)
@app.route("/edituser/<userid>", methods=["GET"])
def edit_user(userid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblusers WHERE userid=%s", (userid,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        flash("❌ User not found!", "danger")
        return redirect(url_for("users_list"))

    return render_template("edit_user.html", user=user)


# Update User (after editing)
@app.route("/updateuser/<userid>", methods=["POST"])
def update_user(userid):
    password = request.form["password"]
    name = request.form["name"]
    mobile = request.form["mobile"]
    emailid = request.form["emailid"]
    usertype = request.form["usertype"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tblusers
        SET password=%s, name=%s, mobile=%s, emailid=%s, usertype=%s
        WHERE userid=%s
    """, (password, name, mobile, emailid, usertype, userid))
    conn.commit()
    conn.close()

    flash("✅ User updated successfully!", "success")
    return redirect(url_for("users_list"))


# Delete User
@app.route("/deleteuser/<userid>", methods=["GET"])
def delete_user(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblusers WHERE userid=%s", (userid,))
    conn.commit()
    conn.close()

    flash("🗑 User deleted successfully!", "success")
    return redirect(url_for("users_list"))

# ------------------- Admin Update Password -------------------
@app.route("/admin/updatepassword", methods=["GET", "POST"])
def admin_updatepassword():
    if "userid" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("admin_updatepassword"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify current password
        cursor.execute("SELECT * FROM tblusers WHERE userid=%s AND password=%s AND usertype='admin'",
                       (session["userid"], current_password))
        user = cursor.fetchone()

        if not user:
            flash("Current password is incorrect!", "danger")
            conn.close()
            return redirect(url_for("admin_updatepassword"))

        # Update with new password
        cursor.execute("UPDATE tblusers SET password=%s WHERE userid=%s",
                       (new_password, session["userid"]))
        conn.commit()
        conn.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for("admin_home"))

    return render_template("admin_updatepassword.html")





# ------------------- Add Patient -------------------
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        patientid = request.form["patientid"]
        password = request.form["password"]
        name = request.form["name"]
        address = request.form["address"]
        mobile = request.form["mobile"]

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tblpatients (patientid, password, name, address, mobile) VALUES (%s, %s, %s, %s, %s)",
                           (patientid, password, name, address, mobile))
            conn.commit()
            flash("Patient added successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        finally:
            conn.close()
        return redirect(url_for("patients_list"))
    return render_template("add_patient.html")


# ------------------- Patients List -------------------
@app.route("/patients_list")
def patients_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblpatients")
    patients = cursor.fetchall()
    conn.close()
    return render_template("patients_list.html", patients=patients)


# ------------------- Edit Patient -------------------
@app.route("/edit_patient/<patientid>")
def edit_patient(patientid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblpatients WHERE patientid=%s", (patientid,))
    patient = cursor.fetchone()
    conn.close()
    return render_template("edit_patient.html", patient=patient)


# ------------------- Update Patient -------------------
@app.route("/update_patient/<patientid>", methods=["POST"])
def update_patient(patientid):
    password = request.form["password"]
    name = request.form["name"]
    address = request.form["address"]
    mobile = request.form["mobile"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""UPDATE tblpatients SET password=%s, name=%s, address=%s, mobile=%s 
                      WHERE patientid=%s""", (password, name, address, mobile, patientid))
    conn.commit()
    conn.close()

    flash("Patient updated successfully!", "success")
    return redirect(url_for("patients_list"))


# ------------------- Delete Patient -------------------
@app.route("/delete_patient/<patientid>")
def delete_patient(patientid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblpatients WHERE patientid=%s", (patientid,))
    conn.commit()
    conn.close()
    flash("Patient deleted successfully!", "success")
    return redirect(url_for("patients_list"))

# ------------------- Receptionist Update Password -------------------
@app.route("/receptionist_updatepassword", methods=["GET", "POST"])
def receptionist_updatepassword():
    if "userid" not in session or session.get("role") != "receptionist":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("receptionist_login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        userid = session["userid"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check current password
        cursor.execute("SELECT * FROM tblusers WHERE userid=%s AND password=%s AND usertype=%s",
                       (userid, current_password, "receptionist"))
        user = cursor.fetchone()

        if not user:
            flash("❌ Current password is incorrect!", "danger")
        elif new_password != confirm_password:
            flash("❌ New password and confirm password do not match!", "danger")
        else:
            cursor.execute("UPDATE tblusers SET password=%s WHERE userid=%s",
                           (new_password, userid))
            conn.commit()
            flash("✅ Password updated successfully!", "success")

        conn.close()

    return render_template("receptionist_updatepassword.html")

# ------------------- Doctor Update Password -------------------
@app.route("/doctor_updatepassword", methods=["GET", "POST"])
def doctor_updatepassword():
    if "userid" not in session or session.get("role") != "doctor":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("doctor_login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        userid = session["userid"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tblusers WHERE userid=%s AND password=%s AND usertype=%s",
                       (userid, current_password, "doctor"))
        user = cursor.fetchone()

        if not user:
            flash("❌ Current password is incorrect!", "danger")
        elif new_password != confirm_password:
            flash("❌ New password and confirm password do not match!", "danger")
        else:
            cursor.execute("UPDATE tblusers SET password=%s WHERE userid=%s",
                           (new_password, userid))
            conn.commit()
            flash("✅ Password updated successfully!", "success")

        conn.close()

    return render_template("doctor_updatepassword.html")


# ------------------- Patient Update Password -------------------
@app.route("/patient_updatepassword", methods=["GET", "POST"])
def patient_updatepassword():
    if "userid" not in session or session.get("role") != "patient":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("patient_login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        userid = session["userid"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tblusers WHERE userid=%s AND password=%s AND usertype=%s",
                       (userid, current_password, "patient"))
        user = cursor.fetchone()

        if not user:
            flash("❌ Current password is incorrect!", "danger")
        elif new_password != confirm_password:
            flash("❌ New password and confirm password do not match!", "danger")
        else:
            cursor.execute("UPDATE tblusers SET password=%s WHERE userid=%s",
                           (new_password, userid))
            conn.commit()
            flash("✅ Password updated successfully!", "success")

        conn.close()

    return render_template("patient_updatepassword.html")


# ------------------- Logout -------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))



# ------------------- Run Application -------------------
#EXECUTION OF THE APPLICATION
if __name__ == "__main__":
    # Only open browser once (avoid duplicate tabs when reloader runs)
    if not is_running_from_reloader():
        webbrowser.open_new_tab("http://127.0.0.1:5000/")

    app.run(port=5000, debug=True)
#END