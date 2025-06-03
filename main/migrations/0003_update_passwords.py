from django.db import migrations
from django.contrib.auth.hashers import make_password

def update_passwords(apps, schema_editor):
    Student = apps.get_model('main', 'Student')
    Faculty = apps.get_model('main', 'Faculty')
    
    # Update passwords for all students
    for student in Student.objects.all():
        student.password = make_password(student.password)
        student.save()
    
    # Update passwords for all faculty
    for faculty in Faculty.objects.all():
        faculty.password = make_password(faculty.password)
        faculty.save()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_add_users_and_alter_course'),
    ]

    operations = [
        migrations.RunPython(update_passwords),
    ]
