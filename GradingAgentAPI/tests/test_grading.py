from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import subprocess
import json


def test_create_assignment_success(client: TestClient):
    """Test creating a new assignment"""
    response = client.post("/assignments", json={"assignment_name": "Test Assignment"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Assignment"


def test_create_duplicate_assignment(client: TestClient):
    """Test that creating duplicate assignment fails"""
    assignment_name = "Duplicate Test"
    client.post("/assignments", json={"assignment_name": assignment_name})

    # Try creating again
    response = client.post("/assignments", json={"assignment_name": assignment_name})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_upload_criteria_json(client: TestClient):
    """Test uploading JSON criteria file"""
    assignment_name = "JSON Test Assignment"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria = {
        "natural_language_rubric": "Grade the binary search implementation. Full marks for correct implementation.",
        "regex_checks": [
            {
                "pattern": "Arrays\\.binarySearch",
                "deduction": 50,
                "message": "Used built-in binary search"
            }
        ]
    }

    response = client.post(
        f"/assignments/{assignment_name}/criteria",
        files={
            "criteria_file": (
                "criteria.json",
                json.dumps(criteria).encode("utf-8"),
                "application/json"
            )
        }
    )

    assert response.status_code == 200
    assert "saved" in response.json()["message"].lower()


def test_upload_criteria_txt(client: TestClient):
    """Test uploading text criteria file"""
    assignment_name = "TXT Test Assignment"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria_text = "This is a natural language rubric for grading."

    response = client.post(
        f"/assignments/{assignment_name}/criteria",
        files={
            "criteria_file": (
                "criteria.txt",
                criteria_text.encode("utf-8"),
                "text/plain"
            )
        }
    )

    assert response.status_code == 200
    assert "saved" in response.json()["message"].lower()


def test_grade_assignment_success(client: TestClient):
    """Test successful grading with mocked Gemini API"""
    # Setup assignment and criteria
    assignment_name = "Grade Test Assignment"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria = {
        "natural_language_rubric": "Evaluate the code quality and design patterns.",
        "regex_checks": [
            {
                "pattern": "System\\.out\\.println",
                "deduction": 5,
                "message": "Used print statements for debugging"
            }
        ]
    }

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

    # Mock the subprocess, file operations, and Gemini API
    with patch("subprocess.run") as mock_run, \
         patch("os.walk") as mock_walk, \
         patch("os.path.isdir") as mock_isdir, \
         patch("builtins.open", new_callable=MagicMock) as mock_open, \
         patch("google.generativeai.configure") as mock_genai_config, \
         patch("google.generativeai.GenerativeModel") as mock_genai_model:

        # Mock git clone
        mock_run.return_value = MagicMock(returncode=0)

        # Mock directory check
        mock_isdir.return_value = True

        # Mock file walking
        mock_walk.return_value = [("/tmp/test", [], ["BinarySearch.java"])]

        # Mock file reading
        mock_file = MagicMock()
        mock_file.read.return_value = 'public class BinarySearch {\n    System.out.println("test");\n}'
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock Gemini API response
        mock_response = MagicMock()
        mock_response.text = "[-10 points] Missing error handling for edge cases\n[-5 points] Code lacks proper documentation"
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_genai_model.return_value = mock_model_instance

        # Make grading request
        response = client.post(
            "/grade",
            json={
                "assignment_name": assignment_name,
                "repo_link": "https://github.com/testuser/repo",
                "token": "test_token",
                "gemini_api_key": "test_gemini_key"
            }
        )

        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Assignment grading complete."
        assert result["student_id"] == "testuser"
        assert "grading_result" in result

        # Grade should be 100 - 5 (regex) - 10 (gemini) - 5 (gemini) = 80
        assert result["grading_result"]["grade"] == 80


def test_grade_assignment_no_criteria(client: TestClient):
    """Test grading when criteria doesn't exist"""
    response = client.post(
        "/grade",
        json={
            "assignment_name": "Nonexistent Assignment",
            "repo_link": "https://github.com/test/repo",
            "token": "test_token",
            "gemini_api_key": "test_key"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_grade_assignment_clone_fails(client: TestClient):
    """Test grading when git clone fails"""
    assignment_name = "Clone Fail Test"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria = {
        "natural_language_rubric": "Test rubric",
        "regex_checks": []
    }

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

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git clone", stderr="fatal: repository not found"
        )

        response = client.post(
            "/grade",
            json={
                "assignment_name": assignment_name,
                "repo_link": "https://github.com/test/nonexistent",
                "token": "test_token",
                "gemini_api_key": "test_key"
            }
        )

    assert response.status_code == 400
    assert "clone" in response.json()["detail"].lower()


def test_grade_assignment_no_java_files(client: TestClient):
    """Test grading when no Java files are found"""
    assignment_name = "No Java Files Test"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria = {
        "natural_language_rubric": "Test rubric",
        "regex_checks": []
    }

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
         patch("os.path.isdir") as mock_isdir, \
         patch("os.walk") as mock_walk:

        mock_run.return_value = MagicMock(returncode=0)
        mock_isdir.return_value = True
        mock_walk.return_value = [("/tmp/test", [], [])]  # No files

        response = client.post(
            "/grade",
            json={
                "assignment_name": assignment_name,
                "repo_link": "https://github.com/test/repo",
                "token": "test_token",
                "gemini_api_key": "test_key"
            }
        )

    assert response.status_code == 404
    assert "no java files" in response.json()["detail"].lower()


def test_get_all_grades(client: TestClient):
    """Test retrieving all grades"""
    response = client.get("/grades")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_student_grades(client: TestClient):
    """Test retrieving grades for a specific student"""
    response = client.get("/grades/testuser")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_student_id_extraction(client: TestClient):
    """Test that student ID is correctly extracted from GitHub URL"""
    assignment_name = "Student ID Test"
    client.post("/assignments", json={"assignment_name": assignment_name})

    criteria = {
        "natural_language_rubric": "Test",
        "regex_checks": []
    }

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

    with patch("subprocess.run"), \
         patch("os.path.isdir", return_value=True), \
         patch("os.walk", return_value=[("/tmp/test", [], ["Test.java"])]), \
         patch("builtins.open", new_callable=MagicMock), \
         patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel"):

        # Mock file reading
        mock_file = MagicMock()
        mock_file.read.return_value = "public class Test {}"

        response = client.post(
            "/grade",
            json={
                "assignment_name": assignment_name,
                "repo_link": "https://github.com/johndoe/my-assignment",
                "token": "test_token",
                "gemini_api_key": "test_key"
            }
        )

        assert response.status_code == 200
        assert response.json()["student_id"] == "johndoe"
