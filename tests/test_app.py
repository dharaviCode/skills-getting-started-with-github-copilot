from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities_returns_activity_data():
    # Arrange
    # No setup required; the API exposes the in-memory activity list.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    # Ensure clean state for the test
    try:
        client.delete(f"/activities/{activity_name}/participants/{email}")
    except Exception:
        pass

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in activities_response.json()[activity_name]["participants"]

    # Cleanup for test isolation
    client.delete(f"/activities/{activity_name}/participants/{email}")


def test_signup_for_activity_rejects_duplicate_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert email not in response.json()["participants"]


def test_unregister_participant_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Does Not Exist"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
