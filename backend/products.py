from flask import Blueprint, render_template, request, redirect , session
import mysql.connector
import os
from werkzeug.utils import secure_filename


products_bp = Blueprint("products", __name__, url_prefix="/products")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2004",
        database="meraki"
    )

@products_bp.route("/", methods=["GET", "POST"])
def products():
    con = connect_db()
    cur = con.cursor()

    # ADD PRODUCT
    if request.method == "POST":
        cur.execute("""
            INSERT INTO product
            (product_ID, product_title, category, supplier, price, available_quantity)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            request.form["product_id"],
            request.form["title"],
            request.form["category"],
            request.form["supplier"],
            request.form["price"],
            request.form["quantity"]
        ))
        con.commit()
        product_id = request.form["product_id"]

        # ===== COLORS =====
        colors = request.form["colors"].split(",")
        for color in colors:
            cur.execute("""
                INSERT INTO product_colors (product_ID, colors)
                VALUES (%s, %s)
            """, (product_id, color.strip()))

        # ===== SIZES =====
        sizes = request.form["sizes"].split(",")
        for size in sizes:
            cur.execute("""
                INSERT INTO product_sizes (product_ID, sizes)
                VALUES (%s, %s)
            """, (product_id, size.strip()))


        images = request.files.getlist("images[]")
        print("IMAGES:", images)


        for img in images:
            if img and img.filename != "":
                filename = secure_filename(img.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                img.save(save_path)

                cur.execute("""
                    INSERT INTO product_images (product_ID, image_path)
                    VALUES (%s, %s)
                """, (product_id, f"uploads/{filename}"))

        con.commit()

    # FETCH PRODUCTS
    cur.execute("""
        SELECT p.product_ID, p.product_title, c.category_name,
                s.supplier_name, p.price, p.available_quantity,
                GROUP_CONCAT(DISTINCT pc.colors) AS colors,
                GROUP_CONCAT(DISTINCT ps.sizes) AS sizes
        FROM product p
        JOIN category c ON p.category = c.category_ID
        JOIN supplier s ON p.supplier = s.supplier_ID
        LEFT JOIN product_colors pc ON p.product_ID = pc.product_ID
        LEFT JOIN product_sizes ps ON p.product_ID = ps.product_ID
        GROUP BY p.product_ID
    """)
    products = cur.fetchall()
    print("PRODUCTS FROM DB:", products)
    cur.execute("SELECT category_ID, category_name FROM category")
    categories = cur.fetchall()

    cur.execute("SELECT supplier_ID, supplier_name FROM supplier")
    suppliers = cur.fetchall()


    con.close()
    return render_template(
        "products.html",
        products=products,
        categories=categories,
        suppliers=suppliers,
        role=session.get("role")
    )

@products_bp.route("/delete/<int:pid>", methods=["POST"])
def delete_product(pid):
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM product WHERE product_ID=%s", (pid,))
    con.commit()
    con.close()
    return redirect("/products")

@products_bp.route("/edit/<int:pid>", methods=["GET", "POST"])
def edit_product(pid):
    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE product
            SET product_title=%s, category=%s, supplier=%s,
                price=%s, available_quantity=%s
            WHERE product_ID=%s
        """, (
            request.form["title"],
            request.form["category"],
            request.form["supplier"],
            request.form["price"],
            request.form["quantity"],
            pid
        ))
        con.commit()

        
        # ===== UPDATE COLORS =====
        cur.execute("DELETE FROM product_colors WHERE product_ID=%s", (pid,))

        colors = request.form.get("colors")
        if colors:
            for color in colors.split(","):
                cur.execute("""
                    INSERT INTO product_colors (product_ID, colors)
                    VALUES (%s, %s)
                """, (pid, color.strip()))

        # ===== UPDATE SIZES =====
        cur.execute("DELETE FROM product_sizes WHERE product_ID=%s", (pid,))

        sizes = request.form.get("sizes")
        if sizes:
            for size in sizes.split(","):
                cur.execute("""
                    INSERT INTO product_sizes (product_ID, sizes)
                    VALUES (%s, %s)
                """, (pid, size.strip()))

        # SAVE NEW PRODUCT IMAGES

        images = request.files.getlist("new_images[]")
        print("NEW IMAGES:", images)


        for img in images:
            if img and img.filename != "":
                filename = secure_filename(img.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                img.save(save_path)

                cur.execute("""
                    INSERT INTO product_images (product_ID, image_path)
                    VALUES (%s, %s)
                """, (pid, f"uploads/{filename}"))


        con.commit()


        con.close()
        return redirect(f"/products/edit/{pid}")


    cur.execute("SELECT * FROM product WHERE product_ID=%s", (pid,))
    product = cur.fetchone()

    cur.execute("SELECT category_ID, category_name FROM category")
    categories = cur.fetchall()

    cur.execute("SELECT supplier_ID, supplier_name FROM supplier")
    suppliers = cur.fetchall()

    # ===== GET PRODUCT =====
    cur.execute("SELECT * FROM product WHERE product_ID=%s", (pid,))
    product = cur.fetchone()

    # ===== GET COLORS =====
    cur.execute("SELECT colors FROM product_colors WHERE product_ID=%s", (pid,))
    colors = cur.fetchall()

    # ===== GET SIZES =====
    cur.execute("SELECT sizes FROM product_sizes WHERE product_ID=%s", (pid,))
    sizes = cur.fetchall()

    colors_str = ", ".join([c[0] for c in colors])
    sizes_str = ", ".join([s[0] for s in sizes])


    cur.execute("""
        SELECT image_ID, image_path
        FROM product_images
        WHERE product_ID = %s
    """, (pid,))
    images = cur.fetchall()


    con.close()
    return render_template(
        "edit_product.html",
        product=product,
        categories=categories,
        suppliers=suppliers,
        images=images,
        colors=colors_str,
        sizes=sizes_str,
        role=session.get("role")
    )

@products_bp.route("/delete-image/<int:image_id>", methods=["POST"])
def delete_image(image_id):
    con = connect_db()
    cur = con.cursor()

    # get image path
    cur.execute(
        "SELECT image_path FROM product_images WHERE image_ID = %s",
        (image_id,)
    )
    img = cur.fetchone()

    if img:
        image_path = img[0]

        # delete file from folder
        full_path = os.path.join(os.path.dirname(__file__), "static", image_path)
        if os.path.exists(full_path):
            os.remove(full_path)

        # delete from DB
        cur.execute(
            "DELETE FROM product_images WHERE image_ID = %s",
            (image_id,)
        )
        con.commit()

    con.close()
    return redirect(request.referrer)
