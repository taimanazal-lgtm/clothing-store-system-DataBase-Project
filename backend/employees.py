from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

employees_bp = Blueprint("employees", __name__)

# =========================
# EMPLOYEES (LIST + ADD)
# =========================
@employees_bp.route("/employees", methods=["GET", "POST"])
def employees():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # -------- ADD --------
    if request.method == "POST":
        emp_id = request.form.get("employee_id")
        name = request.form.get("employee_name")
        position = request.form.get("position")
        salary = request.form.get("salary")
        hours = request.form.get("working_hours")
        branch_id = request.form.get("branch_id")

        cursor.execute("""
            INSERT INTO Employee
            (employee_ID, employee_name, position, salary, working_hours, branch_ID)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (emp_id, name, position, salary, hours, branch_id))

        db.commit()
        return redirect(url_for("employees.employees"))

    # -------- GET EMPLOYEES --------
    cursor.execute("""
        SELECT e.employee_ID, e.employee_name, e.position,
               e.salary, e.working_hours, b.branch_name
        FROM Employee e
        JOIN Branch b ON e.branch_ID = b.branch_ID
    """)
    employees = cursor.fetchall()

    # -------- GET BRANCHES --------
    cursor.execute("SELECT branch_ID, branch_name FROM Branch")
    branches = cursor.fetchall()

    return render_template(
        "employees.html",
        employees=employees,
        branches=branches
    )


# =========================
# DELETE EMPLOYEE
# =========================
@employees_bp.route("/employees/delete/<int:id>", methods=["POST"])
def delete_employee(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM Employee WHERE employee_ID=%s",
        (id,)
    )
    db.commit()

    return redirect(url_for("employees.employees"))


# =========================
# EDIT EMPLOYEE
# =========================
@employees_bp.route("/employees/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form.get("employee_name")
        position = request.form.get("position")
        salary = request.form.get("salary")
        hours = request.form.get("working_hours")
        branch_id = request.form.get("branch_id")

        cursor.execute("""
            UPDATE Employee
            SET employee_name=%s,
                position=%s,
                salary=%s,
                working_hours=%s,
                branch_ID=%s
            WHERE employee_ID=%s
        """, (name, position, salary, hours, branch_id, id))

        db.commit()
        return redirect(url_for("employees.employees"))

    # -------- GET EMPLOYEE --------
    cursor.execute(
        "SELECT * FROM Employee WHERE employee_ID=%s",
        (id,)
    )
    emp = cursor.fetchone()

    # -------- GET BRANCHES --------
    cursor.execute("SELECT branch_ID, branch_name FROM Branch")
    branches = cursor.fetchall()

    return render_template(
        "edit_employee.html",
        emp=emp,
        branches=branches
    )
