from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import subprocess
import json

def test_grade_assignment_success(client: TestClient):
    # Create assignment and criteria
    assignment_name = "Test Assignment"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria = [
        {
            "pattern": "Test",
            "deduction": 10,
            "message": "Use of Test class"
        }
    ]

    client.post(
        f"/assignments/{assignment_name}/criteria",
        files={
            "criteria_file": (
                "criteria.json",
                json.dumps(criteria).encode("utf-8"),
                "application/json"
            )
        }
    )

    with patch("subprocess.run") as mock_run, \
         patch("os.walk") as mock_walk, \
         patch("os.path.isdir") as mock_isdir, \
         patch("builtins.open", new_callable=MagicMock) as mock_open:

        mock_run.return_value = MagicMock(check=True, capture_output=True, text=True)
        mock_walk.return_value = [("/tmp/somedir", [], ["Test.java"])]
        mock_isdir.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "public class Test {}"

        response = client.post(
            "/grade",
            json={
                "assignment_name": assignment_name,
                "repo_link": "https://github.com/test/repo",
                "token": "test_token"
            }
        )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Assignment analysis complete."
    assert response_json["grading_result"]["grade"] == 90
    assert "Use of Test class" in response_json["grading_result"]["feedback"]


def test_grade_assignment_no_criteria(client: TestClient):
    response = client.post(
        "/grade",
        json={
            "assignment_name": "Non-existent Assignment",
            "repo_link": "https://github.com/test/repo",
            "token": "test_token"
        }
    )
    assert response.status_code == 404

def test_grade_assignment_repo_clone_fails(client: TestClient):
    assignment_name = "Test Assignment Clone Fail"
    client.post("/assignments", json={"assignment_name": assignment_name})
    client.post(
        f"/assignments/{assignment_name}/criteria",
        files={
            "criteria_file": (
                "criteria.txt",
                "Test criteria".encode("utf-8"),
                "text/plain"
            )
        }
    )

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git clone", stderr="fatal: repository not found")
        response = client.post(
            "/grade",
            json={
                "assignment_name": assignment_name,
                "repo_link": "https://github.com/test/repo",
                "token": "test_token"
            }
        )
    assert response.status_code == 400

def test_get_all_grades(client: TestClient):
    # First, grade an assignment to create a grade entry
    test_grade_assignment_success(client) 

    response = client.get("/grades")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_student_grades(client: TestClient):
    # First, grade an assignment to create a grade entry
    test_grade_assignment_success(client)

    response = client.get("/grades/student_placeholder")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["student_id"] == "student_placeholder"
