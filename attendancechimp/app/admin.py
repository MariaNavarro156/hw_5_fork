from django.contrib import admin
from app.models import Course, Lecture

admin.site.register(Course)
admin.site.register(Lecture)
#admin.site.register(QRCodeUpload)
#admin.site.register(InstructorProfile)
#admin.site.register(StudentProfile)