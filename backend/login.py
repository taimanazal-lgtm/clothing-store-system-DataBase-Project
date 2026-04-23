from flask import Blueprint, render_template, request, redirect, session, url_for ,flash 
import mysql.connector

login_bp = Blueprint("login", __name__)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]



         # 🔹 Seller login 
        if username == "seller" and password == "2004":
            session.clear()
            session["role"] = "seller"
            return redirect("/seller/home")

        con = connect_db()
        cur = con.cursor(dictionary=True)

        # 🔹 Employee login
        cur.execute("""
            SELECT * FROM Employee
            WHERE employee_name = %s AND employee_ID = %s
        """, (username, password))

        employee = cur.fetchone()

        if employee:
            session.clear()
            session["role"] = "employee"
            session["employee_id"] = employee["employee_ID"]
            con.close()
            return redirect("/employee/home")

        # 🔹 Customer login
        cur.execute("""
            SELECT * FROM Customer
            WHERE email = %s AND password = %s
        """, (username, password))

        customer = cur.fetchone()

        if customer:
            session.clear()
            session["role"] = "customer"
            session["customer_id"] = customer["customer_ID"]
            con.close()
            return redirect(url_for("shop.shop"))

        con.close()
        error = "Invalid login"

    return render_template("login.html", error=error)


# =========================
# REGISTER (NEW CUSTOMER)
# =========================
# =========================
# REGISTER (NEW CUSTOMER)
# =========================
@login_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            con = connect_db()
            cur = con.cursor()

            cur.execute("""
                INSERT INTO Customer (customer_name, email, password)
                VALUES (%s, %s, %s)
            """, (name, email, password))

            con.commit()
            con.close()

            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("login.login"))

        except mysql.connector.Error as err:
            flash(str(err), "error")
            return redirect(url_for("login.register"))

    return render_template("register.html")
