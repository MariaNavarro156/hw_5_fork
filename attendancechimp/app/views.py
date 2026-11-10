"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io
from django.views.decorators.http import require_GET, require_POST

from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
                     Lecture, QRCodeUpload, is_instructor, is_student)

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2 — time, sum 
# ---------------------------------------------------------------------------

@csrf_exempt
def time_view(request):
    """Return the current Chicago time as HH:MM."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    now = datetime.now().astimezone(CDT)
    return HttpResponse(now.strftime("%H:%M"))


@csrf_exempt
def sum_view(request):
    """Return the sum of query parameters n1 and n2."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    try:
        n1 = float(request.GET['n1'])
        n2 = float(request.GET['n2'])
    except (KeyError, ValueError):
        return HttpResponse("Error: provide numeric n1 and n2", status=400)
    result = n1 + n2
    if result == int(result):
        return HttpResponse(str(int(result)))
    return HttpResponse(str(result))


# ---------------------------------------------------------------------------
# HW4  — index, user creation
# ---------------------------------------------------------------------------

def new(request):
    """Render the sign-up form (GET only)."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    return render(request, 'app/new.html')

def index(request):
    """Render the home page (index.html)."""
    now = datetime.now().astimezone(CDT)
    context = {
        'current_time': now.strftime("%H:%M"),
        'user': request.user,
    }
    return render(request, 'app/index.html', context)

@csrf_exempt
def createUser(request):
    """Create a new student or instructor user (POST only)."""
    if request.method != "POST":
        return HttpResponse("Error: only POST is allowed", status=405)
    try:
        user_name = request.POST['user_name']
        password = request.POST['password']
        email = request.POST['email']
        is_student_flag = request.POST.get('is_student', '1')
    except KeyError:
        return HttpResponse("Error: missing required fields", status=400)

    if User.objects.filter(email=email).exists():
        return HttpResponse("Error: email already in use", status=400)
    if User.objects.filter(username=user_name).exists():
        return HttpResponse("Error: user name already in use", status=400)

    user = User.objects.create_user(username=user_name, password=password,
                                    email=email)
    if str(is_student_flag) in ('1', 'true', 'True', 'on'):
        StudentProfile.objects.create(user=user)
    else:
        InstructorProfile.objects.create(user=user)

    user = authenticate(username=user_name, password=password)
    if user is not None:
        login(request, user)
    return HttpResponse("User created successfully", status=200)

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------

def new_course(request):
    """Display the form for creating a new course."""
    return render(request, "app/new_course.html")

@csrf_exempt
@require_POST
def create_course(request):
    if not is_instructor(request.user):
        return HttpResponse("Only instructors can create courses.", status = 401)

    Course.objects.create(
        instructor = request.user,
        name = request.POST.get('course-name'),
        start_time = request.POST.get('start-time'),
        end_time = request.POST.get('end-time'),
        day_mon = "day-mon" in request.POST,
        day_tue = "day-tue" in request.POST,
        day_wed = "day-wed" in request.POST,
        day_thu = "day-thu" in request.POST,
        day_fri = "day-fri" in request.POST,
    )
    return HttpResponse("Course created successfully!", status=200)

def new_lecture(request):
    """Display the form for creating a new lecture."""
    return render(request, "app/new_lecture.html", {"courses": Course.objects.all()})


@csrf_exempt
@require_POST
def create_lecture(request):
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Instructor login required.", status=401)

    course_name = request.POST.get("choice", "")
    course = Course.objects.filter(name=course_name).first()
    if course is None:
        return HttpResponse("Course not found.", status=400)

    Lecture.objects.create(course=course)
    return HttpResponse("Lecture created!", status=200)

def new_qr_upload(request):
    """Display the form for uploading a QR code image."""
    return render(request, "app/new_qr_upload.html")

@csrf_exempt
@require_POST
def create_qr_upload(request):
    if not is_student(request.user):
        return HttpResponse("Only students can upload QR codes.", status=401)

    image = request.FILES.get("imageUpload")
    if image is None:
        return HttpResponse("No file uploaded.", status=400)

    QRCodeUpload.objects.create(student=request.user, image=image)
    return HttpResponse("Upload saved!", status=200)

@require_GET
def dump_uploads(request):
    """Return a JSON dump of all QR code uploads."""
    if not is_instructor(request.user):
        return HttpResponse("Only instructors can view uploads.", status=401)

    data = [
        {
            "username": upload.student.username,
            "upload_time": upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for upload in QRCodeUpload.objects.all()
    ]
    return JsonResponse(data, safe=False)
