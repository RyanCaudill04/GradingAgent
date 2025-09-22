from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json
from .models import Submission
import requests

class FrontendBackendCommunicationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.fastapi_url_grade = "http://fastapi:8001/grade"
        self.fastapi_url_criteria = "http://fastapi:8001/assignments/test_assignment/criteria"
        self.fastapi_url_grades = "http://fastapi:8001/grades"

    @patch('requests.post')
    def test_submit_grading_request_success(self, mock_post):
        # Mock a successful FastAPI response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"grade": "A", "feedback": "Great work!"}
        mock_post.return_value.raise_for_status.return_value = None

        # Simulate a POST request to the Django view
        response = self.client.post(reverse('submit_grading_request'), {
            'assignment_name': 'test_assignment',
            'repo_link': 'https://github.com/test/repo',
            'token': 'test_token'
        })

        # Check if a Submission object was created and saved
        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.first()
        self.assertEqual(submission.assignment_name, 'test_assignment')
        self.assertEqual(submission.status, 'COMPLETED')
        self.assertIsNotNone(submission.fastapi_response)
        self.assertEqual(submission.fastapi_response["grade"], "A")

        # Check if FastAPI was called with the correct payload
        mock_post.assert_called_once_with(
            self.fastapi_url_grade,
            json={
                "assignment_name": 'test_assignment',
                "repo_link": 'https://github.com/test/repo',
                "token": 'test_token'
            },
            timeout=30
        )

        # Check if the user was redirected to the submission detail page
        self.assertRedirects(response, reverse('submission_detail', args=[submission.submission_id]))

    @patch('requests.post')
    def test_submit_grading_request_fastapi_failure(self, mock_post):
        # Mock a failed FastAPI response
        mock_post.return_value.status_code = 500
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.RequestException("FastAPI error")

        # Simulate a POST request
        response = self.client.post(reverse('submit_grading_request'), {
            'assignment_name': 'test_assignment_fail',
            'repo_link': 'https://github.com/test/repo_fail',
            'token': 'test_token_fail'
        })

        # Check if Submission object was created and marked as FAILED
        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.first()
        self.assertEqual(submission.assignment_name, 'test_assignment_fail')
        self.assertEqual(submission.status, 'FAILED')
        self.assertIsNotNone(submission.fastapi_response)
        self.assertIn("error", submission.fastapi_response)

        # Check redirect
        self.assertRedirects(response, reverse('submission_detail', args=[submission.submission_id]))

    # Add more tests for upload_criteria_view, view_grades, and other views
    # For upload_criteria_view, you'll need to mock requests.post with files
    # For view_grades, you'll need to mock requests.get

from io import BytesIO

class CriteriaUploadTests(TestCase):

    def setUp(self):
        self.client = Client()

    @patch('requests.post')
    def test_upload_criteria_view_success(self, mock_post):
        # Mock the response from the backend
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": "Criteria for test_assignment saved."}

        # Create a dummy file for upload
        file_content = b'Test criteria content'
        dummy_file = BytesIO(file_content)
        dummy_file.name = 'criteria.txt'

        # Simulate a POST request to the view
        response = self.client.post(reverse('upload_criteria'), {
            'assignment_name': 'test_assignment',
            'criteria_file': dummy_file
        })

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the success message is in the response context
        self.assertIn('result', response.context)
        self.assertIn('Criteria for test_assignment saved.', response.context['result'])

class OtherViewTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_submission_list_view(self):
        response = self.client.get(reverse('submission_list'))
        self.assertEqual(response.status_code, 200)

    def test_submission_detail_view(self):
        # Create a dummy submission to test the detail view
        submission = Submission.objects.create(
            assignment_name='test_assignment',
            repo_link='https://github.com/test/repo',
            token='test_token',
            status='COMPLETED',
            fastapi_response={"grade": "A", "feedback": "Great work!"}
        )
        response = self.client.get(reverse('submission_detail', args=[submission.submission_id]))
        self.assertEqual(response.status_code, 200)

    @patch('requests.get')
    def test_view_grades_view(self, mock_get):
        # Mock the response from the backend
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "assignment_name": "test_assignment",
                "student_id": "student1",
                "grade": 90,
                "feedback": "Good work"
            }
        ]

        response = self.client.get(reverse('view_grades'))
        self.assertEqual(response.status_code, 200)