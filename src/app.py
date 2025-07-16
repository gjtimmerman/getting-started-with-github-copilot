"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.mergington_school
    activities_collection = db.activities
    # Test connection
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except ConnectionFailure:
    print("Failed to connect to MongoDB")
    raise

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize database with hardcoded activities
def initialize_database():
    """Initialize MongoDB with hardcoded activities if collection is empty"""
    if activities_collection.count_documents({}) == 0:
        initial_activities = [
            {
                "_id": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            {
                "_id": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            },
            {
                "_id": "Gym Class",
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"]
            },
            {
                "_id": "Soccer Team",
                "description": "Join the school soccer team and compete in local leagues",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 18,
                "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
            },
            {
                "_id": "Basketball Club",
                "description": "Practice basketball skills and play friendly matches",
                "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["liam@mergington.edu", "ava@mergington.edu"]
            },
            {
                "_id": "Art Club",
                "description": "Explore painting, drawing, and other visual arts",
                "schedule": "Mondays, 3:30 PM - 5:00 PM",
                "max_participants": 16,
                "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
            },
            {
                "_id": "Drama Society",
                "description": "Participate in acting, stage production, and school plays",
                "schedule": "Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 20,
                "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
            },
            {
                "_id": "Math Olympiad",
                "description": "Prepare for math competitions and solve challenging problems",
                "schedule": "Fridays, 2:00 PM - 3:30 PM",
                "max_participants": 10,
                "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
            },
            {
                "_id": "Science Club",
                "description": "Conduct experiments and explore scientific concepts",
                "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
                "max_participants": 14,
                "participants": ["elijah@mergington.edu", "harper@mergington.edu"]
            }
        ]
        activities_collection.insert_many(initial_activities)
        print("Database initialized with sample activities")
    else:
        print("Database already contains activities")

# Initialize the database on startup
initialize_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities from MongoDB"""
    activities_cursor = activities_collection.find({})
    activities_dict = {}
    for activity in activities_cursor:
        activity_name = activity["_id"]
        # Remove the _id field and create the response format
        activity_data = {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"]
        }
        activities_dict[activity_name] = activity_data
    return activities_dict


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Find the activity in MongoDB
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Already signed up for this activity")
    
    # Check if activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    
    # Add student to activity
    activities_collection.update_one(
        {"_id": activity_name},
        {"$addToSet": {"participants": email}}
    )
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Find the activity in MongoDB
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student not registered for this activity")
    
    # Remove student from activity
    activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    
    return {"message": f"Unregistered {email} from {activity_name}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
