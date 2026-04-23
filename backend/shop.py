from flask import Blueprint, render_template, request, session, redirect, url_for
import mysql.connector




shop_bp = Blueprint("shop", __name__, url_prefix="/shop")

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )

# =========================
# MAIN SHOP PAGE
# =========================
@shop_bp.route("/")
def shop():
    con = connect_db()
    cur = con.cursor()
    
    category_filter = request.args.get('category')
    search_query = request.args.get('search')
    
    query = """
        SELECT 
            p.product_ID,
            p.product_title,
            p.price,
            c.category_name,
            GROUP_CONCAT(DISTINCT pc.colors) AS colors,
            GROUP_CONCAT(DISTINCT ps.sizes) AS sizes,
            MIN(pi.image_path) AS image_path
        FROM Product p
        JOIN Category c ON p.category = c.category_ID
        LEFT JOIN Product_colors pc ON p.product_ID = pc.Product_ID
        LEFT JOIN Product_sizes ps ON p.product_ID = ps.Product_ID
        LEFT JOIN Product_Images pi ON p.product_ID = pi.product_ID
    """
    
    where_clauses = []
    params = []
    
    if category_filter:
        where_clauses.append("c.category_name = %s")
        params.append(category_filter)
    
    if search_query:
        where_clauses.append("p.product_title LIKE %s")
        params.append(f"%{search_query}%")
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " GROUP BY p.product_ID ORDER BY p.product_ID"
    
    cur.execute(query, tuple(params))
    products = cur.fetchall()
    
    cur.execute("SELECT DISTINCT category_name FROM Category")
    categories = [row[0] for row in cur.fetchall()]
    
    con.close()
    
    cart_count = len(session.get('cart', {}))
    
    return render_template(
        "shop.html",
        products=products,
        categories=categories,
        cart_count=cart_count,
        selected_category=category_filter,
        search_query=search_query
    )

# =========================
# PRODUCT DETAILS PAGE
# =========================
@shop_bp.route("/product/<int:product_id>")
def product_details(product_id):
    img_index = int(request.args.get("img", 0))

    con = connect_db()
    cur = con.cursor()

    # product info
    cur.execute("""
        SELECT 
            p.product_ID,
            p.product_title,
            p.price,
            c.category_name
        FROM Product p
        JOIN Category c ON p.category = c.category_ID
        WHERE p.product_ID = %s
    """, (product_id,))
    product = cur.fetchone()

    # product images
    cur.execute("""
        SELECT image_path
        FROM Product_Images
        WHERE product_ID = %s
        ORDER BY image_ID
    """, (product_id,))
    images = [row[0] for row in cur.fetchall()]

    con.close()

    # handle missing product or images
    if not images:
        images = ["images/placeholder.png"]

    if img_index < 0:
        img_index = 0
    if img_index >= len(images):
        img_index = len(images) - 1

    return render_template(
        "product_details.html",
        product=product,
        images=images,
        img_index=img_index,
        cart_count=len(session.get("cart", {}))
    )

# =========================
# CART MANAGEMENT (FIXED)
# =========================
@shop_bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    
    quantity = int(request.form.get('quantity', 1))
    selected_color = request.form.get('color', '')
    selected_size = request.form.get('size', '')
    
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT product_title, price FROM Product WHERE product_ID = %s", (product_id,))
    product_info = cur.fetchone()
    con.close()
    
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'title': product_info[0],
            'price': float(product_info[1]),
            'quantity': quantity,
            'color': selected_color,
            'size': selected_size,
            'product_id': product_id
        }
    
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('shop.shop'))

@shop_bp.route("/cart")
def view_cart():
    cart = session.get('cart', {})
    
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    
    cart_count = len(cart)
    
    return render_template(
        "cart.html",
        cart=cart,
        total=total,
        cart_count=cart_count
    )

@shop_bp.route("/update_cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = session.get("cart", {})

    if str(product_id) in cart:
        action = request.form.get("action")

        if action == "increase":
            cart[str(product_id)]["quantity"] += 1

        elif action == "decrease":
            if cart[str(product_id)]["quantity"] > 1:
                cart[str(product_id)]["quantity"] -= 1

        elif action == "remove":
            del cart[str(product_id)]

    session["cart"] = cart
    return redirect(url_for("shop.view_cart"))


@shop_bp.route("/clear_cart", methods=["POST"])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('shop.view_cart'))

# =========================
# CHECKOUT
# =========================
@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get('cart', {})

    if not cart:
        return redirect(url_for('shop.shop'))

    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        con = connect_db()
        cur = con.cursor()

        # 1️⃣ checking existing customer
        cur.execute(
            "SELECT customer_ID FROM customer WHERE email = %s",
            (email,)
        )
        customer = cur.fetchone()

        if customer:
            customer_id = customer[0]
        else:
            # 2️⃣ adding new customer
            cur.execute(
                "INSERT INTO customer (customer_name, email, password) VALUES (%s, %s, %s)",
                (name, email, "") 
            )
            customer_id = cur.lastrowid

            # 3️⃣ adding address
            cur.execute(
                "INSERT INTO customer_address (customer_ID, address) VALUES (%s, %s)",
                (customer_id, address)
            )

            # 4️⃣ adding phone number
            cur.execute(
                "INSERT INTO customer_phone (customer_ID, phone_number) VALUES (%s, %s)",
                (customer_id, phone)
            )

        # 5️⃣ adding order
        cur.execute("""
            INSERT INTO orders (order_date, payment_status, shipping_status, customer)
            VALUES (NOW(), %s, %s, %s)
        """, ("pending", "processing", customer_id))

        order_id = cur.lastrowid

        # 6️⃣ adding products to order
        for item in cart.values():
            cur.execute("""
                INSERT INTO order_product (order_ID, product_ID, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, item['product_id'], item['quantity']))

        con.commit()
        con.close()

        session.pop('cart', None)
        return redirect(url_for('shop.order_confirmation', order_id=order_id))


    return render_template(
        "checkout.html",
        cart=cart,
        total=total
    )


@shop_bp.route("/order_confirmation/<int:order_id>")
def order_confirmation(order_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM orders WHERE order_ID = %s",
        (order_id,)
    )
    order = cursor.fetchone()

    cursor.close()
    conn.close()

    if not order:
        return redirect(url_for('shop.shop'))

    return render_template("order_confirmation.html", order=order)


# =========================
# ABOUT & CONTACT
# =========================
@shop_bp.route("/about")
def about():
    cart_count = len(session.get('cart', {}))
    return render_template("about.html", cart_count=cart_count)

@shop_bp.route("/contact")
def contact():
    cart_count = len(session.get('cart', {}))
    return render_template("contact.html", cart_count=cart_count)


