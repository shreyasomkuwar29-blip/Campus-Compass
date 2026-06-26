from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import timedelta

app = Flask(__name__)

# Load data
students = pd.read_csv("data/student_dataset.csv")
events = pd.read_csv("data/events_dataset.csv")
interactions = pd.read_csv("data/interaction_dataset.csv")

students.columns = students.columns.str.strip()
events.columns = events.columns.str.strip()
interactions.columns = interactions.columns.str.strip()

events["Date"] = pd.to_datetime(events["Date"], format="%d-%m-%Y", errors="coerce")
events = events.dropna(subset=["Date"])

# -------------------------------
# FUNCTIONS
# -------------------------------

def recommend_by_interest(vibe):
    return events[
        events["Type"].str.lower().str.contains(vibe.lower(), na=False)
    ].sort_values("Date").head(6)

def recommend_from_past(roll):
    user_events = interactions[interactions["Roll_No"] == roll]

    if user_events.empty:
        return None

    similar_users = interactions[
        interactions["Event_Name"].isin(user_events["Event_Name"])
    ]["Roll_No"].unique()

    recommended = interactions[
        (interactions["Roll_No"].isin(similar_users)) &
        (~interactions["Event_Name"].isin(user_events["Event_Name"]))
    ]

    top = recommended["Event_Name"].value_counts().head(5)
    return events[events["Event_Name"].isin(top.index)]

def upcoming_events():
    today = events["Date"].min()
    next_week = today + timedelta(days=7)

    return events[
        (events["Date"] >= today) &
        (events["Date"] <= next_week)
    ].sort_values("Date")

# -------------------------------
# STEP 1 (LOGIN → SHOW PAST)
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        roll = request.form["roll"].strip().upper()

        if roll.isdigit():
            roll = f"RBU{int(roll):03d}"

        student = students[students["Roll_No"] == roll]

        if student.empty:
            return render_template("index.html", error="Student not found!")

        name = student.iloc[0]["Name"]

        past_events = interactions[
            interactions["Roll_No"] == roll
        ]["Event_Name"].unique()

        return render_template(
            "step2.html",
            name=name,
            roll=roll,
            past_events=past_events
        )

    return render_template("index.html")

# -------------------------------
# STEP 2 (ENTER INTEREST)
# -------------------------------
@app.route("/dashboard", methods=["POST"])
def dashboard():
    roll = request.form["roll"]
    vibe = request.form["vibe"]

    student = students[students["Roll_No"] == roll]
    name = student.iloc[0]["Name"]

    past_events = interactions[
        interactions["Roll_No"] == roll
    ]["Event_Name"].unique()

    interest = recommend_by_interest(vibe)
    past_rec = recommend_from_past(roll)

    today = events["Date"].min()
    upcoming_list = []

    for _, e in upcoming_events().iterrows():
        e_dict = e.to_dict()
        e_dict["days_left"] = (e["Date"] - today).days
        upcoming_list.append(e_dict)

    return render_template(
        "dashboard.html",
        name=name,
        roll=roll,
        past_events=past_events,
        interest_events=interest.to_dict("records"),
        past_recommend=None if past_rec is None else past_rec.to_dict("records"),
        upcoming=upcoming_list
    )

# -------------------------------
# REGISTER FEATURE 🔥
# -------------------------------
@app.route("/register", methods=["POST"])
def register():
    roll = request.form["roll"]
    event_name = request.form["event"]

    global interactions

    new_entry = pd.DataFrame([[roll, event_name]], columns=["Roll_No", "Event_Name"])

    interactions = pd.concat([interactions, new_entry], ignore_index=True)

    interactions.to_csv("data/interaction_dataset.csv", index=False)

    return redirect(url_for("index"))

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)