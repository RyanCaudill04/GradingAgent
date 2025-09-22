from django.db import models
import uuid

class Submission(models.Model):
    submission_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_name = models.CharField(max_length=255, blank=True, null=True)
    assignment_name = models.CharField(max_length=255)
    repo_link = models.URLField(max_length=2000)
    token = models.CharField(max_length=255, blank=True, null=True)
    submission_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='PENDING') # PENDING, PROCESSING, COMPLETED, FAILED
    fastapi_response = models.JSONField(blank=True, null=True)
    # You might want to add a user foreign key here if you have user authentication

    def __str__(self):
        return f"Submission {self.submission_id} - {self.assignment_name} ({self.status})"