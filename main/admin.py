from django.contrib import admin
from django import forms
from .models import Student, Faculty, Course, Department, Announcement,Material

class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ('student_id','role')
    exclude = ('course',)  # Remove course field from form
    
    def save_model(self, request, obj, form, change):
        # Save the student object
        super().save_model(request, obj, form, change)
        
        # Automatically assign courses based on department
        if obj.department:
            courses = Course.objects.filter(department=obj.department)
            obj.course.set(courses)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('department')

class FacultyAdmin(admin.ModelAdmin):
    readonly_fields = ('faculty_id', 'role', 'display_password')

    def display_password(self, obj):
        return obj.password
    display_password.short_description = 'Password'

class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ('code',)

class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ('department_id',)

admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Department,DepartmentAdmin)
admin.site.register(Announcement)
admin.site.register(Material)