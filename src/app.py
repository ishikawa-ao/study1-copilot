"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from pathlib import Path

app = FastAPI(title="スタディ1 API",
              description="このAPIはFastAPIの機能を学習するために使用されます。")

# Pydantic models for request/response
class ActivityCreate(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int

class ActivityResponse(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "チェスクラブ": {
        "description": "戦略を学び、チェスのトーナメントで競い合う",
        "schedule": "金曜日 午後3時30分～午後5時",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "プログラミング教室": {
        "description": "プログラミングの基礎を学び、ソフトウェアプロジェクトを構築する",
        "schedule": "火曜日と木曜日 午後3時30分～午後4時30分",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "体育教室": {
        "description": "体育とスポーツ活動",
        "schedule": "月曜日、水曜日、金曜日 午後2時～午後3時",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities")
def create_activity(activity: ActivityCreate):
    """新しいアクティビティを作成する"""
    # Check if activity already exists
    if activity.name in activities:
        raise HTTPException(status_code=409, detail="アクティビティは既に存在します")

    # Create new activity
    new_activity = {
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "participants": []
    }
    activities[activity.name] = new_activity
    return {"message": "アクティビティが正常に作成されました", "activity": {"name": activity.name, **new_activity}}


@app.delete("/activities/{activity_name}")
def delete_activity(activity_name: str):
    """Delete an activity"""
    # Check if activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="アクティビティが見つかりません")

    # Delete the activity
    deleted_activity = activities.pop(activity_name)
    return {"message": f"Activity '{activity_name}' 削除されました", "activity": {"name": activity_name, **deleted_activity}}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """生徒をアクティビティに登録する"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="アクティビティが見つかりません")

    # Get the specific activity
    activity = activities[activity_name]

    # 大文字と小文字、空白の重複を避けるため、メールアドレスを正規化してください。
    email = email.strip().lower()

    # 既に登録されているかどうかを確認してください（正規化されたものを比較してください）。
    if email in [p.lower() for p in activity["participants"]]:
        raise HTTPException(status_code=409, detail="このアクティビティにはすでに登録済みです")

    # Check if activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="アクティビティは満席です")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
