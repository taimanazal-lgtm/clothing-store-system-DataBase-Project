from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )

# =========================
# CUSTOMER DASHBOARD
# =========================
@customer_bp.route("/home")
def customer_home():
    if session.get("role") != "customer":
        return redirect(url_for("login.login"))
    

    
    return redirect(url_for("shop.shop"))


# =========================
# CUSTOMER ORDERS
# =========================
@customer_bp.route("/orders")
def customer_orders():
    if session.get("role") != "customer":
        return redirect(url_for("login.login"))
    
    con = connect_db()
    cur = con.cursor(dictionary=True)
    
    customer_id = session.get("customer_id")
    
    cur.execute("""
        SELECT o.order_ID, o.order_date, o.payment_status, 
               o.shipping_status,
               IFNULL(SUM(op.quantity * p.price), 0) AS total
        FROM Orders o
        LEFT JOIN Order_product op ON o.order_ID = op.order_ID
        LEFT JOIN Product p ON op.product_ID = p.product_ID
        WHERE o.customer = %s
        GROUP BY o.order_ID
        ORDER BY o.order_date DESC
    """, (customer_id,))
    orders = cur.fetchall()
    
    con.close()
    
    return render_template("customer_orders.html", orders=orders)

# =========================
# VIEW ORDER DETAILS
# =========================
@customer_bp.route("order/<int:order_id>")
def view_order(order_id):
    if session.get("role") != "customer":
        return redirect(url_for("login.login"))
    
    con = connect_db()
    cur = con.cursor(dictionary=True)
    
    customer_id = session.get("customer_id")
    
    
    cur.execute("SELECT * FROM Orders WHERE order_ID=%s AND customer=%s", 
               (order_id, customer_id))
    order = cur.fetchone()
    
    if not order:
        flash("Order not found", "error")
        return redirect(url_for("customer.customer_orders"))

    cur.execute("""
        SELECT p.product_ID, p.product_title, op.quantity, 
               p.price, (op.quantity * p.price) AS total
        FROM Order_product op
        JOIN Product p ON op.product_ID = p.product_ID
        WHERE op.order_ID = %s
    """, (order_id,))
    products = cur.fetchall()
    

    cur.execute("""
        SELECT d.delivery_status, d.shipping_date, e.employee_name
        FROM Delivery d
        JOIN Employee e ON d.responsible_employee = e.employee_ID
        WHERE d.orders = %s
    """, (order_id,))
    delivery = cur.fetchone()
    
    con.close()
    
    return render_template(
        "customer_order_details.html",
        order=order,
        products=products,
        delivery=delivery
    )

# =========================
# CUSTOMER PROFILE
# =========================
@customer_bp.route("/profile")
def customer_profile():
    if session.get("role") != "customer":
        return redirect(url_for("login.login"))

    con = connect_db()
    cur = con.cursor(dictionary=True)

    customer_id = session["customer_id"]

    # Customer basic info
    cur.execute("""
        SELECT customer_name, email, password
        FROM Customer
        WHERE customer_ID = %s
    """, (customer_id,))
    customer = cur.fetchone()

    # Phones
    cur.execute("""
        SELECT phone_number 
        FROM Customer_phone 
        WHERE customer_ID = %s
    """, (customer_id,))
    phones = cur.fetchall()

    # Addresses
    cur.execute("""
        SELECT address 
        FROM Customer_address 
        WHERE customer_ID = %s
    """, (customer_id,))
    addresses = cur.fetchall()

    con.close()

    return render_template(
        "my_info.html",
        customer=customer,
        phones=phones,
        addresses=addresses
    )

@customer_bp.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if session.get("role") != "customer":
        return redirect(url_for("login.login"))

    customer_id = session.get("customer_id")
    con = connect_db()
    cur = con.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        # تحديث customer
        cur.execute("""
            UPDATE Customer 
            SET customer_name=%s, email=%s
            WHERE customer_ID=%s
        """, (name, email, customer_id))

        # phone
        cur.execute("DELETE FROM Customer_phone WHERE customer_ID=%s", (customer_id,))
        if phone:
            cur.execute("""
                INSERT INTO Customer_phone (customer_ID, phone_number)
                VALUES (%s,%s)
            """, (customer_id, phone))

        # address
        cur.execute("DELETE FROM Customer_address WHERE customer_ID=%s", (customer_id,))
        if address:
            cur.execute("""
                INSERT INTO Customer_address (customer_ID, address)
                VALUES (%s,%s)
            """, (customer_id, address))

        con.commit()
        con.close()
        return redirect(url_for("customer.customer_profile"))

    # GET
    cur.execute("SELECT * FROM Customer WHERE customer_ID=%s", (customer_id,))
    customer = cur.fetchone()

    cur.execute("SELECT phone_number FROM Customer_phone WHERE customer_ID=%s", (customer_id,))
    phone = cur.fetchone()

    cur.execute("SELECT address FROM Customer_address WHERE customer_ID=%s", (customer_id,))
    address = cur.fetchone()

    con.close()

    return render_template(
        "edit_profile.html",
        customer=customer,
        phone=phone,
        address=address
    )

@customer_bp.route("/profile/change-password", methods=["GET", "POST"])
def change_password():
    if session.get("role") != "customer":
        return redirect(url_for("login.login"))

    customer_id = session.get("customer_id")
    con = connect_db()
    cur = con.cursor(dictionary=True)

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

       
        cur.execute(
            "SELECT password FROM Customer WHERE customer_ID=%s",
            (customer_id,)
        )
        customer = cur.fetchone()

        
        if not check_password_hash(customer["password"], current_password):
            con.close()
            return render_template(
                "change_password.html",
                error="Current password is incorrect"
            )

        if new_password != confirm_password:
            con.close()
            return render_template(
                "change_password.html",
                error="Passwords do not match"
            )

        hashed_password = generate_password_hash(new_password)

        cur.execute(
            "UPDATE Customer SET password=%s WHERE customer_ID=%s",
            (hashed_password, customer_id)
        )
        con.commit()
        con.close()

        return redirect(url_for("customer.customer_profile"))

    con.close()
    return render_template("change_password.html")

# =========================
# LOGOUT
# =========================
@customer_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login"))
    
