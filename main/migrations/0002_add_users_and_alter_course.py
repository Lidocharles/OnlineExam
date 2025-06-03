from django.db import migrations, models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def create_users(apps, schema_editor):
    Student = apps.get_model('main', 'Student')
    Faculty = apps.get_model('main', 'Faculty')
    
    # Create User objects for all existing students
    for student in Student.objects.all():
        User.objects.create_user(
            username=f'student_{student.student_id}',
            password=make_password(student.password)
        )
    
    # Create User objects for all existing faculty
    for faculty in Faculty.objects.all():
        User.objects.create_user(
            username=f'faculty_{faculty.faculty_id}',
            password=make_password(faculty.password)
        )

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_users),
        migrations.AlterField(
            model_name='student',
            name='course',
            field=models.ManyToManyField(
                related_name='students',
                blank=True,
                editable=False,
                to='main.Course'
            ),
        ),
    ]
