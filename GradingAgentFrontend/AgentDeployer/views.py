from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.http import JsonResponse
import json
from .models import Submission # Import the Submission model
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def fetch_data_from_fastapi(request):
    fastapi_url = settings.FASTAPI_URL

    try:
        response = requests.get(fastapi_url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(data)

def submit_grading_request(request):
    if request.method == 'POST':
        assignment_name = request.POST.get('assignment_name')
        repo_link = request.POST.get('repo_link')
        token = request.POST.get('token')

        # 1. Create Submission instance with PENDING status
        submission = Submission.objects.create(
            assignment_name=assignment_name,
            repo_link=repo_link,
            token=token,
            status='PENDING'
        )

        fastapi_url = f"{settings.FASTAPI_URL}/grade"
        payload = {
            "assignment_name": assignment_name,
            "repo_link": repo_link,
            "token": token
        }

        try:
            response = requests.post(fastapi_url, json=payload, timeout=30)
            response.raise_for_status()
            fastapi_result = response.json()
            # 3. Update Submission with COMPLETED status and FastAPI response
            submission.status = 'COMPLETED'
            submission.fastapi_response = fastapi_result
            submission.save()
            result = json.dumps(fastapi_result, indent=4)
        except requests.RequestException as e:
            # 3. Update Submission with FAILED status and error
            submission.status = 'FAILED'
            submission.fastapi_response = {"error": str(e)}
            submission.save()
            result = json.dumps({"error": str(e)}, indent=4)

        # Redirect to the submission detail page
        return redirect('submission_detail', submission_id=submission.submission_id)
    return render(request, 'submit_grading_request.html', {'result': None})

def upload_criteria_view(request):
    result = None
    if request.method == 'POST':
        assignment_name = request.POST.get('assignment_name')
        criteria_file = request.FILES.get('criteria_file')

        if assignment_name and criteria_file:
            # Create the assignment first
            fastapi_url_create = f"{settings.FASTAPI_URL}/assignments"
            payload = {"assignment_name": assignment_name}
            try:
                response = requests.post(fastapi_url_create, json=payload, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                if response.status_code != 400:
                    result = json.dumps({"error": str(e)}, indent=4)
                    return render(request, 'upload_criteria.html', {'result': result})

            # Then upload the criteria
            fastapi_url_upload = f"{settings.FASTAPI_URL}/assignments/{assignment_name}/criteria"
            files = {'criteria_file': (criteria_file.name, criteria_file.read(), criteria_file.content_type)}

            try:
                response = requests.post(fastapi_url_upload, files=files, timeout=10)
                response.raise_for_status()
                result = json.dumps(response.json(), indent=4)
            except requests.RequestException as e:
                result = json.dumps({"error": str(e)}, indent=4)
        else:
            result = json.dumps({"error": "Assignment name and criteria file are required."}, indent=4)

    return render(request, 'upload_criteria.html', {'result': result})

def view_grades(request):
    assignments = Submission.objects.values_list('assignment_name', flat=True).distinct()
    return render(request, 'view_grades.html', {'assignments': assignments})

def submission_list(request):
    submissions = Submission.objects.all().order_by('-submission_time')
    return render(request, 'submission_list.html', {'submissions': submissions})

def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, submission_id=submission_id)
    return render(request, 'submission_detail.html', {'submission': submission})

def assignment_detail(request, assignment_name):
    submissions = Submission.objects.filter(assignment_name=assignment_name)
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', '-submission_time')

    if search_query:
        submissions = submissions.filter(student_name__icontains=search_query)

    if sort_by == 'student_name':
        submissions = submissions.order_by('student_name')
    elif sort_by == 'final_grade':
        submissions = sorted(submissions, key=lambda s: s.fastapi_response.get('final_grade', 0))
    else:
        submissions = submissions.order_by(sort_by)

    return render(request, 'assignment_detail.html', {
        'submissions': submissions, 
        'assignment_name': assignment_name,
        'search_query': search_query,
    })

def student_grades(request, student_name):
    fastapi_url = f"{settings.FASTAPI_URL}/grades/{student_name}"
    try:
        response = requests.get(fastapi_url, timeout=10)
        response.raise_for_status()
        grades = response.json()
    except requests.RequestException as e:
        grades = [{"error": str(e)}]

    return render(request, 'student_grades.html', {'grades': grades, 'student_name': student_name})
