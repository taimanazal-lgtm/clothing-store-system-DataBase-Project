from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

branches_bp = Blueprint("branches", __name__)


@branches_bp.route("/branches", methods=["GET", "POST"])
def branches():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # -------- ADD / UPDATE --------
    if request.method == "POST":
        action = request.form.get("action")
        branch_id = request.form.get("branch_id")
        name = request.form.get("branch_name")
        city = request.form.get("city")

        if action == "add":
            cursor.execute(
                "INSERT INTO branch (branch_ID, branch_name, city) VALUES (%s,%s,%s)",
                (branch_id, name, city)
            )

        elif action == "update":
            cursor.execute(
                "UPDATE branch SET branch_name=%s, city=%s WHERE branch_ID=%s",
                (name, city, branch_id)
            )

        db.commit()

        return redirect(url_for("branches.branches"))


    # -------- DELETE --------
    delete_id = request.args.get("delete")
    if delete_id:
        cursor.execute("DELETE FROM branch WHERE branch_ID=%s", (delete_id,))
        db.commit()
        return redirect(url_for("branches.branches"))

    # -------- GET DATA --------
    cursor.execute("SELECT * FROM branch")
    branches = cursor.fetchall()
    

    # -------- EDIT --------
    edit_branch = None
    edit_id = request.args.get("edit")
    if edit_id:
        cursor.execute("SELECT * FROM branch WHERE branch_ID=%s", (edit_id,))
        edit_branch = cursor.fetchone()

    return render_template("branches.html",
                           branches=branches,
                           edit_branch=edit_branch)
