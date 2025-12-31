from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Task
from dotenv import load_dotenv
load_dotenv()
from config import Config
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


def login_required(fn):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/", methods=["GET"])
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "User already exists", 400

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return "Invalid credentials", 401

        session["user_id"] = user.id
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    user_id = session["user_id"]

    if request.method == "POST":
        data = request.get_json()
        task = Task(content=data["content"], user_id=user_id)
        db.session.add(task)
        db.session.commit()
        return jsonify({"id": task.id, "content": task.content, "completed": task.completed})

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": t.id, "content": t.content, "completed": t.completed}
        for t in tasks
    ])


@app.route("/tasks/<int:task_id>", methods=["PUT", "DELETE"])
@login_required
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != session["user_id"]:
        return "Forbidden", 403

    if request.method == "PUT":
        task.completed = not task.completed
        db.session.commit()
        return jsonify({"completed": task.completed})

    db.session.delete(task)
    db.session.commit()
    return "", 204


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if not user:
            return "User not found", 404
        return redirect(url_for("reset_password", username=username))
    return render_template("forgot_password.html")


@app.route("/reset_password/<username>", methods=["GET", "POST"])
def reset_password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match", 400

        user.set_password(password)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("reset_password.html")


@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return "Invalid credentials", 401

        Task.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("delete_account.html")

