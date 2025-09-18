#===========================================================
# Client Tracker
# Azaria Lee
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================


from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.auth    import login_required
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps

#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():

    if "logged_in" in session:
        user_id = session["user_id"]

        with connect_db() as client:
            # Get all the things from the DB
            sql = """
            SELECT clients.id,
                   clients.name,
                   clients.phone,
                   clients.address
            FROM clients
            JOIN users ON clients.user_id = users.id
            WHERE users.id = ?;
            """
            params=[user_id]
            result = client.execute(sql, params)
            clients = result.rows

            # And show them on the page
            return render_template("pages/home.jinja", clients=clients)
    else:
        return render_template("pages/home.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
# @app.get("/things/")
# def show_all_things():
#     with connect_db() as client:
#         # Get all the things from the DB
#         sql = """
#             SELECT things.id,
#                    things.name,
#                    users.name AS owner

#             FROM things
#             JOIN users ON things.user_id = users.id

#             ORDER BY things.name ASC
#         """
#         params=[]
#         result = client.execute(sql, params)
#         things = result.rows

#         # And show them on the page
#         return render_template("pages/things.jinja", things=things)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB, including the owner info
        sql = """
            SELECT things.id,
                   things.name,
                   things.price,
                   things.user_id,
                   users.name AS owner

            FROM things
            JOIN users ON things.user_id = users.id

            WHERE things.id=?
        """
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/thing.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for add client page
#-----------------------------------------------------------
@app.get("/client-add")
@login_required
def client_add_form():
    return render_template("pages/client-add.jinja")


#-----------------------------------------------------------
# Route for adding a client when form submitted
#-----------------------------------------------------------
@app.post("/client-add")
@login_required
def add_a_client():
    name    = html.escape(request.form.get("name"))
    phone   = html.escape(request.form.get("phone"))
    address = html.escape(request.form.get("address"))
    user_id = session["user_id"]

    with connect_db() as client:
        sql = "INSERT INTO clients (name, phone, address, user_id) VALUES (?, ?, ?, ?)"
        params = [name, phone, address, user_id]
        client.execute(sql, params)

    flash(f"Client '{name}' added", "success")
    return redirect("/")


#-----------------------------------------------------------
# Route for editing a client
#-----------------------------------------------------------
@app.get("/client-edit/<int:client_id>")
@login_required
def edit_a_client(client_id):
    if "logged_in" in session:
        user_id =  session["user_id"]

    with connect_db() as client:
        sql = """
        SELECT id, name, phone, address
        FROM clients WHERE id = ?
        """

        params = [client_id]
        result = client.execute(sql, params)
        rows = result.rows
        client_info = rows[0] if rows else None

    if client_info is None:
        flash("Client not found", "error")
        return redirect("/")
    else:
        return render_template("pages/client-edit.jinja", client=client_info)


#-----------------------------------------------------------
# Route for saving edited client
#-----------------------------------------------------------
@app.post("/client-edit/<int:client_id>")
@login_required
def save_client(client_id):
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    with connect_db() as client:
        sql = """
        UPDATE clients
        SET name = ?, phone = ?, address = ?
        WHERE id = ?
        """
        params = [name, phone, address, client_id]
        client.execute(sql, params)

    flash(f"Client '{name}' updated", "success")
    return redirect("/")


#-----------------------------------------------------------
# Route for deleting a client, Id given in the route
# - Restricted to logged in users
#-----------------------------------------------------------
@app.get("/delete/<int:client_id>")
@login_required
def delete_a_client(client_id):
    # Get the user id from the session
    user_id = session["user_id"]

    with connect_db() as client:
        # Delete the thing from the DB only if we own it
        sql = """
        DELETE FROM clients 
        WHERE id=? AND user_id=?
        """
        params = [client_id, user_id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Client deleted", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
# - Restricted to logged in users
#-----------------------------------------------------------
# @app.get("/delete/<int:id>")
# @login_required
# def delete_a_thing(id):
#     # Get the user id from the session
#     user_id = session["user_id"]

#     with connect_db() as client:
#         # Delete the thing from the DB only if we own it
#         sql = "DELETE FROM things WHERE id=? AND user_id=?"
#         params = [id, user_id]
#         client.execute(sql, params)

#         # Go back to the home page
#         flash("Thing deleted", "success")
#         return redirect("/things")


#-----------------------------------------------------------
# Route for client jobs
#-----------------------------------------------------------
@app.get("/job-info/<int:client_id>")
@login_required
def job_info(client_id):

        user_id = session["user_id"]

        with connect_db() as client:
            # Get all the things from the DB
            sql = """
            SELECT 
                jobs.id,
                jobs.date,
                jobs.name,
                jobs.hours_worked,
                jobs.billed,
                jobs.paid,
                jobs.client_id,
                clients.name AS client_name
            FROM jobs
            JOIN clients ON jobs.client_id = clients.id
            WHERE clients.user_id = ? AND clients.id = ?;
            """
            params=[user_id, client_id]
            result = client.execute(sql, params)
            jobs = result.rows

            client_name = jobs[0]["client_name"] if jobs else None

        # Show the info on correct page
        return render_template("pages/job-info.jinja", jobs=jobs, client_id=client_id, client_name=client_name)


#-----------------------------------------------------------
# Route for checking billed box
#-----------------------------------------------------------
@app.post("/job-toggle-billed/<int:job_id>")
@login_required
def toggle_job_billed(job_id):
    user_id = session["user_id"]

    with connect_db() as client:
        sql = """
        UPDATE jobs
        SET billed = CASE billed
                        WHEN 1 THEN 0
                        ELSE 1
                     END
        WHERE id=? AND client_id IN (
        SELECT id FROM clients WHERE user_id=?
        )
        """

        params = [job_id, user_id]
        client.execute(sql, params)

        flash("Billed updated", "success")
        return redirect(request.referrer or "/")


#-----------------------------------------------------------
# Route for checking paid box
#-----------------------------------------------------------
@app.post("/job-toggle-paid/<int:job_id>")
@login_required
def toggle_job_paid(job_id):
    user_id = session["user_id"]

    with connect_db() as client:
        sql = """
        UPDATE jobs
        SET paid = CASE paid
                        WHEN 1 THEN 0
                        ELSE 1
                     END
        WHERE id=? AND client_id IN (
        SELECT id FROM clients WHERE user_id=?
        )
        """

        params = [job_id, user_id]
        client.execute(sql, params)

        flash("Paid updated", "success")
        return redirect(request.referrer or "/")


#-----------------------------------------------------------
# Route for adding a job when form submitted
#-----------------------------------------------------------
@app.post("/job-add/<int:client_id>")
@login_required
def add_a_job(client_id):
    name         = request.form.get("name")
    hours_worked = request.form.get("hours_worked")
    billed       = 1 if request.form.get("billed") else 0
    paid         = 1 if request.form.get("paid") else 0
    user_id = session["user_id"]

    with connect_db() as client:
        sql = """
        INSERT INTO jobs (client_id, name, hours_worked, billed, paid)
        VALUES (?, ?, ?, ?, ?)
        """
        params = [client_id, name, hours_worked, billed, paid]
        client.execute(sql, params)

    flash(f"Job '{name}' added", "success")
    return redirect(f"/job-info/{client_id}")


#-----------------------------------------------------------
# Route for editing a job
#-----------------------------------------------------------
@app.get("/job-edit/<int:client_id>/<int:job_id>")
@login_required
def edit_a_job(client_id, job_id):
    user_id =  session["user_id"]

    with connect_db() as client:
        sql = """
        SELECT id, name, hours_worked, billed, paid, client_id
        FROM jobs WHERE id = ? AND client_id = ?
        """

        params = [job_id, client_id]
        result = client.execute(sql, params)
        rows = result.rows
        job = rows[0] if rows else None

    if job is None:
        flash("Job not found", "error")
        return redirect(f"/job-info/{client_id}")
    return render_template("pages/job-edit.jinja", job=job, client_id=client_id)


#-----------------------------------------------------------
# Route for saving edited job
#-----------------------------------------------------------
@app.post("/job-edit/<int:client_id>/<int:job_id>")
@login_required
def save_job(client_id, job_id):
    name = request.form.get("name")
    hours_worked = request.form.get("hours_worked")
    billed       = 1 if request.form.get("billed") else 0
    paid         = 1 if request.form.get("paid") else 0

    with connect_db() as client:
        sql = """
        UPDATE jobs
        SET name = ?, hours_worked  = ?, billed = ?, paid = ?
        WHERE id = ? AND client_id = ?
        """
        params = [name, hours_worked, billed, paid, job_id, client_id]
        client.execute(sql, params)

    flash(f"Job '{name}' updated", "success")
    return redirect(f"/job-info/{client_id}")


#-----------------------------------------------------------
# Route for deleting a job, Id given in the route
# - Restricted to logged in users
#-----------------------------------------------------------
@app.get("/delete/<int:client_id>/<int:job_id>")
@login_required
def delete_a_job(client_id, job_id):
    # Get the user id from the session
    user_id = session["user_id"]

    with connect_db() as client:
        # Delete the job from the DB only if we own it
        sql = """
        DELETE FROM jobs 
        WHERE id=? 
            AND client_id IN (
                SELECT id FROM clients WHERE id=? AND user_id=?
            )
        """
        params = [job_id, client_id, user_id]
        client.execute(sql, params)

        # Go back to the job page
        flash("Job deleted", "success")
        return redirect(f"/job-info/{client_id}")


#-----------------------------------------------------------
# User registration form route
#-----------------------------------------------------------
@app.get("/register")
def register_form():
    return render_template("pages/register.jinja")


#-----------------------------------------------------------
# User login form route
#-----------------------------------------------------------
@app.get("/login")
def login_form():
    return render_template("pages/login.jinja")


#-----------------------------------------------------------
# Route for adding a user when registration form submitted
#-----------------------------------------------------------
@app.post("/add-user")
def add_user():
    # Get the data from the form
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")

    with connect_db() as client:
        # Attempt to find an existing record for that user
        sql = "SELECT * FROM users WHERE username = ?"
        params = [username]
        result = client.execute(sql, params)

        # No existing record found, so safe to add the user
        if not result.rows:
            # Sanitise the name
            name = html.escape(name)

            # Salt and hash the password
            hash = generate_password_hash(password)

            # Add the user to the users table
            sql = "INSERT INTO users (name, username, password_hash) VALUES (?, ?, ?)"
            params = [name, username, hash]
            client.execute(sql, params)

            # And let them know it was successful and they can login
            flash("Registration successful", "success")
            return redirect("/login")

        # Found an existing record, so prompt to try again
        flash("Username already exists. Try again...", "error")
        return redirect("/register")


#-----------------------------------------------------------
# Route for processing a user login
#-----------------------------------------------------------
@app.post("/login-user")
def login_user():
    # Get the login form data
    username = request.form.get("username")
    password = request.form.get("password")

    with connect_db() as client:
        # Attempt to find a record for that user
        sql = "SELECT * FROM users WHERE username = ?"
        params = [username]
        result = client.execute(sql, params)

        # Did we find a record?
        if result.rows:
            # Yes, so check password
            user = result.rows[0]
            hash = user["password_hash"]

            # Hash matches?
            if check_password_hash(hash, password):
                # Yes, so save info in the session
                session["user_id"]   = user["id"]
                session["user_name"] = user["name"]
                session["logged_in"] = True

                # And head back to the home page
                flash("Login successful", "success")
                return redirect("/")

        # Either username not found, or password was wrong
        flash("Invalid credentials", "error")
        return redirect("/login")


#-----------------------------------------------------------
# Route for processing a user logout
#-----------------------------------------------------------
@app.get("/logout")
def logout():
    # Clear the details from the session
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("logged_in", None)

    # And head back to the home page
    flash("Logged out successfully", "success")
    return redirect("/")

