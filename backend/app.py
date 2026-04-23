from flask import Flask, render_template, redirect, url_for, session
from login import login_bp
from employees import employees_bp
from branches import branches_bp
from orders import orders_bp
from products import products_bp
from shop import shop_bp
from customer import customer_bp

app = Flask(__name__)
app.secret_key = "meraki_secret"


app.register_blueprint(login_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(branches_bp)
app.register_blueprint(orders_bp) 
app.register_blueprint(products_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(customer_bp)


@app.route("/")
def index():
    role = session.get("role")

    if role == "seller":
        return redirect("/seller/home")
    elif role == "employee":
        return redirect("/employee/home")
    elif role == "customer":
        return redirect(url_for("customer.customer_home"))

    return redirect("/login")


@app.route("/seller/home")
def seller_home():
    if session.get("role") != "seller":
        return redirect(url_for("login.login"))
    return render_template("main.html", role=session.get("role"))


@app.route("/employee/home")
def employee_home():
    if session.get("role") != "employee":
        return redirect(url_for("login.login"))
    return render_template("main.html", role=session.get("role"))





@app.route("/branches")
def branches():
    if session.get("role") != "seller":
        return redirect(url_for("login.login"))
    return render_template("Branches.html")


if __name__ == "__main__":
    app.run(debug=True) 
