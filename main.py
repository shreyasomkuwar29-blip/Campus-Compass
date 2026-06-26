import pandas as pd
from datetime import datetime, timedelta

# -------------------------------
# 📂 Load Datasets
# -------------------------------
try:
    students = pd.read_csv("data/student_dataset.csv")
    events = pd.read_csv("data/events_dataset.csv")
    interactions = pd.read_csv("data/interaction_dataset.csv")
    print("✅ System Ready!")
except Exception as e:
    print("❌ Error loading files:", e)
    exit()

# -------------------------------
# 🧹 Clean Column Names
# -------------------------------
students.columns = students.columns.str.strip()
events.columns = events.columns.str.strip()
interactions.columns = interactions.columns.str.strip()

# -------------------------------
# 📅 Convert Date
# -------------------------------
events["Date"] = pd.to_datetime(events["Date"], format="%d-%m-%Y", errors='coerce')
events = events.dropna(subset=["Date"])
events["Date"] = events["Date"].dt.date

# -------------------------------
# 🧾 Print Event
# -------------------------------
def print_event(event):
    print(f"\n📌 {event['Event_Name']}")
    print(f"   Type: {event['Type']}")
    print(f"   Description: {event['Description']}")
    print(f"   Date: {event['Date'].strftime('%d-%m-%Y')}")
    print(f"   Time: {event['Time']}")
    
    if 'Agenda' in event and pd.notna(event['Agenda']):
        print(f"   🔹 What will happen: {event['Agenda']}")

# -------------------------------
# 📜 Past Events
# -------------------------------
def show_past_events(roll_no):
    past = interactions[interactions["Roll_No"] == roll_no]

    print("\n📜 Your Past Participated Events:")
    if past.empty:
        print("No past events found.")
    else:
        for event in past["Event_Name"].unique():
            print("-", event)

# -------------------------------
# 🔍 VIBE-BASED SEARCH
# -------------------------------
def recommend_by_interest(user_interest):
    keywords = user_interest.lower().split()

    mask = events["Type"].astype(str).str.lower().apply(
        lambda x: any(word in x for word in keywords)
    )

    filtered = events[mask].sort_values(by='Date')

    print("\n🔍 Events Matching Your Vibe:")
    if filtered.empty:
        print("No matching events found.")
    else:
        for _, event in filtered.head(5).iterrows():
            print_event(event)

# -------------------------------
# 🤝 RECOMMEND FROM PAST
# -------------------------------
def recommend_from_past(roll_no):
    print("\n🤝 Recommended Based on Your Past Participation:")

    user_events = interactions[interactions["Roll_No"] == roll_no]

    if user_events.empty:
        print("⚠ No past participation")
        return False

    similar_users = interactions[
        interactions["Event_Name"].isin(user_events["Event_Name"])
    ]["Roll_No"].unique()

    recommended = interactions[
        (interactions["Roll_No"].isin(similar_users)) &
        (~interactions["Event_Name"].isin(user_events["Event_Name"]))
    ]

    top_events = recommended["Event_Name"].value_counts().head(5)

    if top_events.empty:
        print("No strong recommendations")
        return False

    for event_name in top_events.index:
        event_data = events[events["Event_Name"] == event_name]
        if not event_data.empty:
            print_event(event_data.iloc[0])

    return True

# -------------------------------
# 🔥 TRENDING EVENTS
# -------------------------------
def trending_events():
    print("\n🔥 Trending Events:")

    trending = interactions["Event_Name"].value_counts().head(5)

    if trending.empty:
        print("No trending data available.")
        return

    for event_name in trending.index:
        event_data = events[events["Event_Name"] == event_name]
        if not event_data.empty:
            print_event(event_data.iloc[0])

# -------------------------------
# 📅 UPCOMING EVENTS
# -------------------------------
def upcoming_events():
    print("\n📅 Upcoming Events (Next 7 Days):")

    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    upcoming = events[
        (events["Date"] >= today) &
        (events["Date"] <= next_week)
    ].sort_values("Date")

    if upcoming.empty:
        print("No events this week.")
    else:
        for _, event in upcoming.iterrows():
            print_event(event)
            days_left = (event["Date"] - today).days
            print(f"   ⏳ Starts in: {days_left} day(s)")

# -------------------------------
# 🎯 MAIN SYSTEM
# -------------------------------
def run_system():
    roll = input("Enter Roll Number (e.g., 1 or RBU001): ").strip().upper()

    if roll.isdigit():
        roll = f"RBU{int(roll):03d}"

    student = students[students["Roll_No"] == roll]

    if student.empty:
        print("❌ Student not found!")
        return

    name = student.iloc[0]["Name"]
    print(f"\n👋 Welcome {name}!")

    show_past_events(roll)

    user_interest = input("\nEnter your vibe (coding, music, business, etc.): ")

    recommend_by_interest(user_interest)

    has_recommendation = recommend_from_past(roll)

    if not has_recommendation:
        print("👉 Showing trending events instead:")
        trending_events()

    upcoming_events()

# -------------------------------
# ▶ RUN
# -------------------------------
if __name__ == "__main__":
    run_system()


    