from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

# =========================
# DB CONNECTION
# =========================
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )

# =========================
# ORDERS (ADD + VIEW + TOTAL PRICE)
# =========================
@orders_bp.route("/", methods=["GET", "POST"])
def orders():
    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO Orders (order_date, payment_status, shipping_status, customer)
            VALUES (%s, %s, %s, %s)
        """, (
            request.form["order_date"],
            request.form["payment_status"],
            request.form["shipping_status"],
            request.form["customer"]
        ))
        con.commit()

    cur.execute("""
        SELECT 
            o.order_ID,
            o.order_date,
            o.payment_status,
            o.shipping_status,
            c.customer_name,
            IFNULL(SUM(op.quantity * p.price), 0) AS total_price
        FROM Orders o
        JOIN Customer c ON o.customer = c.customer_ID
        LEFT JOIN Order_product op ON o.order_ID = op.order_ID
        LEFT JOIN Product p ON op.product_ID = p.product_ID
        GROUP BY o.order_ID
    """)
    orders = cur.fetchall()

    cur.execute("SELECT customer_ID, customer_name FROM Customer")
    customers = cur.fetchall()

    con.close()
    return render_template(
        "orders.html",
        orders=orders,
        customers=customers,
        role=session.get("role")
    )

# =========================
# ORDER DETAILS
# =========================
@orders_bp.route("/order/<int:order_id>")
def order_details(order_id):
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT 
            p.product_ID,
            p.product_title,
            op.quantity,
            p.price,
            (op.quantity * p.price) AS total
        FROM Order_product op
        JOIN Product p ON op.product_ID = p.product_ID
        WHERE op.order_ID = %s
    """, (order_id,))
    products = cur.fetchall()

    con.close()
    return render_template(
        "order_details.html",
        products=products,
        order_id=order_id,
        role=session.get("role")
    )

# =========================
# ADD PRODUCT TO ORDER
# =========================
@orders_bp.route("/order/<int:order_id>/add_product", methods=["GET", "POST"])
def add_product_to_order(order_id):
    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])

        cur.execute(
            "SELECT available_quantity FROM Product WHERE product_ID=%s",
            (product_id,)
        )
        available = cur.fetchone()[0]

        if available < quantity:
            con.close()
            return "Not enough stock", 400

        cur.execute("""
            SELECT quantity FROM Order_product
            WHERE order_ID=%s AND product_ID=%s
        """, (order_id, product_id))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE Order_product
                SET quantity = quantity + %s
                WHERE order_ID=%s AND product_ID=%s
            """, (quantity, order_id, product_id))
        else:
            cur.execute("""
                INSERT INTO Order_product (order_ID, product_ID, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, product_id, quantity))

        cur.execute("""
            UPDATE Product
            SET available_quantity = available_quantity - %s
            WHERE product_ID = %s
        """, (quantity, product_id))

        con.commit()
        con.close()
        return redirect(url_for("orders.order_details", order_id=order_id))

    cur.execute("SELECT product_ID, product_title FROM Product")
    products = cur.fetchall()

    con.close()
    return render_template(
        "add_product_to_order.html",
        order_id=order_id,
        products=products,
        role=session.get("role")
    )

# =========================
# EDIT PRODUCT IN ORDER
# =========================
@orders_bp.route("/edit_product/<int:order_id>/<int:product_id>", methods=["GET", "POST"])
def edit_product(order_id, product_id):
    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE Order_product
            SET quantity=%s
            WHERE order_ID=%s AND product_ID=%s
        """, (
            request.form["quantity"],
            order_id,
            product_id
        ))
        con.commit()
        con.close()
        return redirect(url_for("orders.order_details", order_id=order_id))

    cur.execute("""
        SELECT quantity FROM Order_product
        WHERE order_ID=%s AND product_ID=%s
    """, (order_id, product_id))
    quantity = cur.fetchone()[0]

    con.close()
    return render_template(
        "edit_product.html",
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        role=session.get("role")
    )

# =========================
# DELETE PRODUCT FROM ORDER
# =========================
@orders_bp.route("/delete_product/<int:order_id>/<int:product_id>", methods=["POST"])
def delete_product(order_id, product_id):
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        DELETE FROM Order_product
        WHERE order_ID=%s AND product_ID=%s
    """, (order_id, product_id))

    con.commit()
    con.close()
    return redirect(url_for("orders.order_details", order_id=order_id))

# =========================
# DELIVERY
# =========================
@orders_bp.route("/delivery/<int:order_id>", methods=["GET", "POST"])
def delivery(order_id):
    con = connect_db()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM Delivery WHERE orders=%s", (order_id,))
    delivery = cur.fetchone()

    if request.method == "POST":
        if delivery:
            cur.execute("""
                UPDATE Delivery
                SET shipping_date=%s,
                    delivery_status=%s,
                    responsible_employee=%s
                WHERE orders=%s
            """, (
                request.form["shipping_date"],
                request.form["delivery_status"],
                request.form["employee"],
                order_id
            ))
        else:
            cur.execute("""
                INSERT INTO Delivery
                (orders, shipping_date, delivery_status, responsible_employee)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                request.form["shipping_date"],
                request.form["delivery_status"],
                request.form["employee"]
            ))

        con.commit()
        con.close()
        return redirect(url_for("orders.delivery", order_id=order_id))

    cur.execute("""
        SELECT employee_ID, employee_name
        FROM Employee
        WHERE position IN ('driver', 'delivery')
    """)
    employees = cur.fetchall()

    con.close()
    return render_template(
        "delivery.html",
        order_id=order_id,
        delivery=delivery,
        employees=employees,
        role=session.get("role")
    )

# =========================
# EDIT ORDER
# =========================
@orders_bp.route("/edit_order/<int:order_id>", methods=["GET", "POST"])
def edit_order(order_id):
    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE Orders
            SET order_date=%s,
                payment_status=%s,
                shipping_status=%s,
                customer=%s
            WHERE order_ID=%s
        """, (
            request.form["order_date"],
            request.form["payment_status"],
            request.form["shipping_status"],
            request.form["customer"],
            order_id
        ))
        con.commit()
        con.close()
        return redirect(url_for("orders.orders"))

    cur.execute("SELECT * FROM Orders WHERE order_ID=%s", (order_id,))
    order = cur.fetchone()

    cur.execute("SELECT customer_ID, customer_name FROM Customer")
    customers = cur.fetchall()

    con.close()
    return render_template(
        "edit_order.html",
        order=order,
        customers=customers,
        role=session.get("role")
    )

# =========================
# DELETE ORDER
# =========================
@orders_bp.route("/delete/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    con = connect_db()
    cur = con.cursor()

    cur.execute("DELETE FROM Order_product WHERE order_ID=%s", (order_id,))
    cur.execute("DELETE FROM Delivery WHERE orders=%s", (order_id,))
    cur.execute("DELETE FROM Orders WHERE order_ID=%s", (order_id,))

    con.commit()
    con.close()
    return redirect(url_for("orders.orders"))