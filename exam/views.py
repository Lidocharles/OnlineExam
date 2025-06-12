from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Quiz, Question, StudentAnswer
from main.models import Student, Course, Faculty
from main.views import is_faculty_authorised, is_student_authorised
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, F, FloatField, Q, Prefetch
from django.db.models.functions import Cast
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import csv
import datetime

def quiz(request, code):
    if not request.user.is_authenticated:
        return redirect('std_login')
    
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            if request.method == 'POST':
                # Handle form submission for creating a quiz
                title = request.POST.get('title')
                description = request.POST.get('description')
                start_str = request.POST.get('start')
                end_str = request.POST.get('end')
                
                # Convert date strings to datetime objects
                try:
                    start = datetime.datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
                    end = datetime.datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid date format. Please use YYYY-MM-DDTHH:MM format.')
                    return redirect('quiz', code=code)
                
                # Handle publish status checkbox
                publish_status = request.POST.get('checkbox') == 'True'
                
                quiz = Quiz(
                    title=title,
                    description=description,
                    start=start,
                    end=end,
                    publish_status=publish_status,
                    course=course
                )
                quiz.save()
                
                # Redirect to the 'addQuestion' view with the new quiz ID
                return redirect('addQuestion', code=code, quiz_id=quiz.id)
            else:
                current_datetime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
                return render(request, 'quiz/quiz.html', {
                    'course': course,
                    'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id']),
                    'current_datetime': current_datetime
                })

        else:
            messages.error(request, 'You are not authorized to access this course.')
            return redirect('std_login')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'error.html')

def addQuestion(request, code, quiz_id):
    if not request.user.is_authenticated:
        return redirect('std_login')
    
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            quiz = Quiz.objects.get(id=quiz_id)
            if request.method == 'POST':
                # Handle form submission for adding a question
                question_text = request.POST.get('question')
                marks = request.POST.get('marks')
                explanation = request.POST.get('explanation')
                question_format = request.POST.get('question_format')

                # Create a new question based on the selected format
                if question_format == 'TF':
                    is_true = request.POST.get('is_true') == 'True'
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, is_true=is_true)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    return redirect('addQuestion', code=code, quiz_id=quiz_id)
                else:
                    messages.error(request, 'Invalid question format.')
                    return redirect('addQuestion', code=code, quiz_id=quiz_id)
            else:
                return render(request, 'quiz/addQuestion.html', {
                    'course': course,
                    'quiz': quiz
                })
        else:
            messages.error(request, 'You are not authorized to access this course.')
            return redirect('std_login')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('std_login')
    except Quiz.DoesNotExist:
        messages.error(request, 'Quiz not found.')
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'error.html')

@login_required
def addQuestion(request, code, quiz_id):
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            quiz = Quiz.objects.get(id=quiz_id)
            if request.method == 'POST':
                # Handle form submission for adding a question
                question_text = request.POST.get('question')
                marks = request.POST.get('marks')
                explanation = request.POST.get('explanation')
                question_format = request.POST.get('question_format')

                # Create a new question based on the selected format
                if question_format == 'TF':
                    is_true = request.POST.get('is_true') == 'True'
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, is_true=is_true)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    if 'saveOnly' in request.POST:
                        return redirect('allQuizzes', code=code)
                    else:
                        return redirect('addQuestion', code=code, quiz_id=quiz_id)

                elif question_format == 'MCQ':
                    option1 = request.POST.get('option1')
                    option2 = request.POST.get('option2')
                    option3 = request.POST.get('option3')
                    option4 = request.POST.get('option4')
                    correct_answer = request.POST.get('correct_answer')
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, option1=option1, option2=option2,
                                        option3=option3, option4=option4, correct_answer=correct_answer)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    if 'saveOnly' in request.POST:
                        return redirect('allQuizzes', code=code)
                    else:
                        return redirect('addQuestion', code=code, quiz_id=quiz_id)

                elif question_format == 'FIB':
                    correct_answer_fib = request.POST.get('correct_answer_fib')
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, correct_answer=correct_answer_fib)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    if 'saveOnly' in request.POST:
                        return redirect('allQuizzes', code=code)
                    else:
                        return redirect('addQuestion', code=code, quiz_id=quiz_id)

                else:
                    messages.error(request, 'Invalid question format.')
                    return redirect('addQuestion', code=code, quiz_id=quiz_id)

            else:
                return render(request, 'quiz/addQuestion.html', {
                    'course': course,
                    'quiz': quiz,
                    'faculty': Faculty.objects.get(
                        faculty_id=request.session['faculty_id'])
                })

        else:
            messages.error(request, 'You are not authorized to access this course.')
            return redirect('std_login')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('std_login')
    except Quiz.DoesNotExist:
        messages.error(request, 'Quiz not found.')
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'error.html')
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            quiz = Quiz.objects.get(id=quiz_id)
            if request.method == 'POST':
                # Handle form submission for adding a question
                question_text = request.POST.get('question')
                marks = request.POST.get('marks')
                explanation = request.POST.get('explanation')
                question_format = request.POST.get('question_format')

                # Create a new question based on the selected format
                if question_format == 'TF':
                    is_true = request.POST.get('is_true') == 'True'
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, is_true=is_true)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    if 'saveOnly' in request.POST:
                        return redirect('allQuizzes', code=code)
                    else:
                        return redirect('addQuestion', code=code, quiz_id=quiz_id)

                elif question_format == 'MCQ':
                    option1 = request.POST.get('option1')
                    option2 = request.POST.get('option2')
                    option3 = request.POST.get('option3')
                    option4 = request.POST.get('option4')
                    correct_answer = request.POST.get('correct_answer')
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, option1=option1, option2=option2,
                                        option3=option3, option4=option4, correct_answer=correct_answer)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    if 'saveOnly' in request.POST:
                        return redirect('allQuizzes', code=code)
                    else:
                        return redirect('addQuestion', code=code, quiz_id=quiz_id)

                elif question_format == 'FIB':
                    correct_answer_fib = request.POST.get('correct_answer_fib')
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, correct_answer=correct_answer_fib)
                    question.save()
                    messages.success(request, 'Question added successfully.')
                    if 'saveOnly' in request.POST:
                        return redirect('allQuizzes', code=code)
                    else:
                        return redirect('addQuestion', code=code, quiz_id=quiz_id)

                else:
                    messages.error(request, 'Invalid question format.')
                    return redirect('addQuestion', code=code, quiz_id=quiz_id)

            else:
                return render(request, 'quiz/addQuestion.html', {
                    'course': course,
                    'quiz': quiz,
                    'faculty': Faculty.objects.get(
                        faculty_id=request.session['faculty_id'])
                })

        else:
            messages.error(request, 'You are not authorized to access this course.')
            return redirect('std_login')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('std_login')
    except Quiz.DoesNotExist:
        messages.error(request, 'Quiz not found.')
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'error.html')

def allQuizzes(request, code):
    if not request.user.is_authenticated:
        return redirect('std_login')
    
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        quizzes = Quiz.objects.filter(course=course)
        
        # Calculate quiz status and total questions
        for quiz in quizzes:
            quiz.total_questions = Question.objects.filter(quiz=quiz).count()
            if quiz.start < datetime.datetime.now():
                quiz.started = True
            else:
                quiz.started = False
            quiz.save()

        # Add total questions for active quizzes
        for quiz in quizzes:
            quiz.total_questions = quiz.question_set.count()

        return render(request, 'quiz/allQuizzes.html', {
            'course': course,
            'quizzes': quizzes,
            'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id'])
        })
    else:
        messages.error(request, 'You are not authorized to access this course.')
        return redirect('std_login')

@login_required
def myQuizzes(request, code):
    try:
        course = Course.objects.get(code=code)
        if is_student_authorised(request, code):
            student = Student.objects.get(student_id=request.session['student_id'])
            quizzes = Quiz.objects.filter(course=course)
            
            # Split quizzes into active and previous
            active_quizzes = []
            previous_quizzes = []
            student = Student.objects.get(student_id=request.session['student_id'])
            
            for quiz in quizzes:
                student_answers = quiz.studentanswer_set.filter(student=student)
                quiz.attempted = student_answers.exists()
                
                if quiz.attempted:
                    # Quiz has been attempted by the student
                    previous_quizzes.append(quiz)
                elif quiz.end < timezone.now():
                    # Quiz has ended but not attempted
                    previous_quizzes.append(quiz)
                else:
                    # Quiz is still active
                    active_quizzes.append(quiz)

            # For previous quizzes, calculate marks and submission time
            for quiz in previous_quizzes:
                student_answers = quiz.studentanswer_set.filter(student=student)
                
                if quiz.attempted:
                    total_marks_obtained = sum([student_answer.marks for student_answer in student_answers])
                    quiz.total_marks_obtained = total_marks_obtained
                    quiz.total_marks = sum([question.marks for question in quiz.question_set.all()])
                    quiz.percentage = round(total_marks_obtained / quiz.total_marks * 100, 2) if quiz.total_marks != 0 else 0
                    quiz.total_questions = quiz.question_set.count()
                    
                    # Get the latest submission time
                    latest_submission = student_answers.order_by('-submission_time').first()
                    if latest_submission and latest_submission.submission_time:
                        quiz.submission_time = latest_submission.submission_time.strftime("%a, %d-%b-%y at %I:%M %p")
                    else:
                        quiz.submission_time = "Not available"
                else:
                    quiz.total_marks_obtained = 0
                    quiz.total_marks = sum([question.marks for question in quiz.question_set.all()])
                    quiz.percentage = 0
                    quiz.total_questions = quiz.question_set.count()
                    quiz.submission_time = "Not attempted"

            # Add total questions for active quizzes
            for quiz in active_quizzes:
                quiz.total_questions = quiz.question_set.count()

            return render(request, 'quiz/myQuizzes.html', {
                'course': course,
                'active_quizzes': active_quizzes,
                'previous_quizzes': previous_quizzes,
                'student': student
            })
        else:
            messages.error(request, 'You are not authorized to access this course.')
            return redirect('std_login')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('std_login')
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'error.html')


def startQuiz(request, code, quiz_id):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        total_questions = questions.count()

        marks = 0
        for question in questions:
            marks += question.marks
        quiz.total_marks = marks

        return render(request, 'quiz/portalStdNew.html',
                      {'course': course, 'quiz': quiz, 'questions': questions, 'total_questions': total_questions,
                       'student': Student.objects.get(student_id=request.session['student_id'])})
    else:
        return redirect('std_login')

def studentAnswer(request, code, quiz_id):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        student = Student.objects.get(student_id=request.session['student_id'])
        
        # Get all questions for this quiz
        questions = Question.objects.filter(quiz=quiz)
        
        # Process each question's answer
        for question in questions:
            answer = request.POST.get(str(question.id))
            
            # Skip if no answer was provided
            if not answer:
                continue
                
            marks = 0
            
            # Calculate marks based on question type
            if question.format == 'MCQ':
                marks = question.marks if answer == question.correct_answer else 0
            elif question.format == 'TF':
                marks = question.marks if answer == str(question.is_true) else 0
            elif question.format == 'FIB':
                student_answer_text = answer.strip().lower()
                correct_answer_text = question.correct_answer.strip().lower()
                
                # Split into words and compare each word
                student_words = student_answer_text.split()
                correct_words = correct_answer_text.split()
                
                # Check if all words match
                marks = question.marks if student_words == correct_words else 0
                answer = student_answer_text  # Store normalized version for consistent display

            # Save or update the student's answer
            student_answer, created = StudentAnswer.objects.update_or_create(
                student=student,
                quiz=quiz,
                question=question,
                defaults={
                    'answer': answer,
                    'marks': marks,
                    'submission_time': timezone.now()
                }
            )
            
            # If this is the first answer being submitted, update quiz submission time
            if created:
                quiz.submission_time = timezone.now()
                quiz.save()

        # Redirect to quiz result page after processing all answers
        try:
            # First, create/update submission time for each question
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            for student_answer in student_answers:
                student_answer.submission_time = timezone.now()
                student_answer.save()

            # Get the latest submission time for this quiz
            latest_submission = student_answers.order_by('-submission_time').first()
            if latest_submission:
                quiz.submission_time = latest_submission.submission_time
                quiz.save()

            # Redirect to myQuizzes page
            return redirect('myQuizzes', code=code)
        except Exception as e:
            messages.error(request, f"Error submitting quiz: {str(e)}")
            return redirect('myQuizzes', code=code)
    else:
        return redirect('std_login')

def download_exam_results(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        try:
            course = Course.objects.get(code=code)
            quiz = Quiz.objects.get(id=quiz_id)
            
            # Get all students in the course
            all_students = Student.objects.filter(course=course)
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            filename = f"{quiz.title.replace(' ', '_')}_results_{timezone.now().strftime('%Y%m%d')}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            writer = csv.writer(response)
            
            # Write header row
            writer.writerow([
                'Exam Name', 'Exam Date', 'Subject',
                'Student Name', 'Student ID', 'Department', 'Email',
                'Status', 'Marks Obtained', 'Total Marks'
            ])
            
            # Calculate total marks for the quiz
            total_marks = sum(question.marks for question in quiz.question_set.all())
            
            # Write data rows for all students
            for student in all_students:
                student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
                
                if student_answers.exists():
                    total_marks_obtained = sum(student_answer.marks for student_answer in student_answers)
                    status = "Attempted"
                else:
                    total_marks_obtained = 0
                    status = "Did not attempt"
                
                writer.writerow([
                    quiz.title,
                    quiz.end.strftime('%Y-%m-%d'),
                    course.name,
                    student.name,
                    student.student_id,
                    student.department,
                    student.email,
                    status,
                    total_marks_obtained,
                    total_marks
                ])
            
            return response
            
        except Quiz.DoesNotExist:
            messages.error(request, 'Quiz not found.')
            return redirect('myQuizzes', code=code)
        except Exception as e:
            messages.error(request, f'Error downloading results: {str(e)}')
            return redirect('myQuizzes', code=code)

    messages.error(request, 'You are not authorized to access this course.')
    return redirect('std_login')

def quizResult(request, code, quiz_id):
    if is_student_authorised(request, code):
        try:
            course = Course.objects.get(code=code)
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            messages.error(request, 'This quiz has been deleted by the faculty.')
            return redirect('myQuizzes', code=code)
        questions = Question.objects.filter(quiz=quiz)

        try:
            student = Student.objects.get(student_id=request.session['student_id'])
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            total_marks_obtained = sum(student_answer.marks for student_answer in student_answers)

            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = sum(question.marks for question in questions)

            if quiz.total_marks != 0:
                quiz.percentage = (total_marks_obtained / quiz.total_marks) * 100
                quiz.percentage = round(quiz.percentage, 2)
            else:
                quiz.percentage = 0

        except Student.DoesNotExist:
            quiz.total_marks_obtained = 0
            quiz.total_marks = 0
            quiz.percentage = 0

        # Get student answers for each question
        for question in questions:
            try:
                student_answer = StudentAnswer.objects.get(student=student, question=question)
                question.student_answer = student_answer.answer if student_answer.answer else "Not answered"
                question.student_marks = student_answer.marks
                
                # Calculate correct/wrong answers for each question
                if question.format == 'MCQ':
                    question.is_correct = question.correct_answer == student_answer.answer
                elif question.format == 'TF':
                    question.is_correct = str(question.is_true) == student_answer.answer
                elif question.format == 'FIB':
                    student_answer_text = student_answer.answer.strip().lower()
                    correct_answer_text = question.correct_answer.strip().lower()
                    student_words = student_answer_text.split()
                    correct_words = correct_answer_text.split()
                    question.is_correct = student_words == correct_words
            except StudentAnswer.DoesNotExist:
                question.student_answer = "Not answered"
                question.student_marks = 0
                question.is_correct = False

            # Set correct answer based on question format
            if question.format == 'TF':
                question.correct_answer = 'True' if question.is_true else 'False'
            elif question.format == 'MCQ':
                question.correct_answer = question.correct_answer
            elif question.format == 'FIB':
                question.correct_answer = question.correct_answer.strip().lower()

        # Check if exam is attempted
        student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
        attempted = student_answers.count() > 0

        # Calculate marks if attempted
        if attempted:
            total_marks_obtained = sum(student_answer.marks for student_answer in student_answers)
            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = sum(question.marks for question in questions)

            if quiz.total_marks != 0:
                quiz.percentage = (total_marks_obtained / quiz.total_marks) * 100
                quiz.percentage = round(quiz.percentage, 2)
            else:
                quiz.percentage = 0

            # Get submission time
            quiz_submission = student_answers.order_by('-submission_time').first()
            if quiz_submission and quiz_submission.submission_time:
                # Calculate time taken only if start time exists
                if quiz.start:
                    time_diff = quiz_submission.submission_time - quiz.start
                    quiz.time_taken = time_diff.total_seconds()
                    quiz.time_taken = round(quiz.time_taken, 2)
                else:
                    quiz.time_taken = 0

                quiz.submission_time = quiz_submission.submission_time.strftime("%a, %d-%b-%y at %I:%M %p")
            else:
                quiz.time_taken = 0
                quiz.submission_time = "Not attempted"
        else:
            quiz.total_marks_obtained = 0
            quiz.total_marks = sum(question.marks for question in questions)
            quiz.percentage = 0
            quiz.time_taken = 0
            quiz.submission_time = "Not attempted"

        return render(request, 'quiz/quizResult.html',
                      {'course': course, 'quiz': quiz, 'questions': questions, 'student': student})
    else:
        return redirect('std_login')

def quizSummary(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)

        questions = Question.objects.filter(quiz=quiz)
        time = datetime.datetime.now()
        total_students = Student.objects.filter(course=course).count()

        # Inside your view function

        for question in questions:
            if question.format == 'MCQ':
                question.A_count = StudentAnswer.objects.filter(question=question, answer='A').count()
                question.B_count = StudentAnswer.objects.filter(question=question, answer='B').count()
                question.C_count = StudentAnswer.objects.filter(question=question, answer='C').count()
                question.D_count = StudentAnswer.objects.filter(question=question, answer='D').count()
            elif question.format == 'TF':
                # Add logic for True/False questions
                question.True_count = StudentAnswer.objects.filter(question=question, answer='True').count()
                question.False_count = StudentAnswer.objects.filter(question=question, answer='False').count()
            elif question.format == 'FIB':
                # Add logic for Fill in the Blank questions
                # Using case-insensitive comparison
                question.correct_answers_count = StudentAnswer.objects.filter(question=question).filter(
                    answer__iexact=question.correct_answer).count()
                question.incorrect_answers_count = StudentAnswer.objects.filter(question=question).exclude(
                    answer__iexact=question.correct_answer).count()

        # Students who have attempted the quiz and their marks
        students = Student.objects.filter(course=course)
        for student in students:
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            total_marks_obtained = 0
            for student_answer in student_answers:
                total_marks_obtained += student_answer.marks
            student.total_marks_obtained = total_marks_obtained

        if request.method == 'POST':
            quiz.publish_status = True
            quiz.save()
            return redirect('quizSummary', code=code, quiz_id=quiz.id)

        # Check if the student has attempted the quiz
        for student in students:
            student.attempted = StudentAnswer.objects.filter(student=student, quiz=quiz).count() > 0

        for student in students:
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            for student_answer in student_answers:
                student.submission_time = student_answer.created_at.strftime("%a, %d-%b-%y at %I:%M %p")

        context = {
            'course': course,
            'quiz': quiz,
            'questions': questions,
            'time': time,
            'total_students': total_students,
            'students': students,
            'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id'])
        }
        return render(request, 'quiz/quizSummaryFaculty.html', context)

    else:
        return redirect('std_login')


# Add the following function to your views.py
def editQuiz(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = get_object_or_404(Quiz, id=quiz_id)

        if request.method == 'POST':
            # Handle form submission to update quiz details
            title = request.POST.get('title')
            description = request.POST.get('description')
            start = request.POST.get('start')
            end = request.POST.get('end')
            publish_status = request.POST.get('checkbox')

            # Update quiz details
            quiz.title = title
            quiz.description = description
            quiz.start = start
            quiz.end = end
            quiz.publish_status = publish_status
            quiz.save()

            messages.success(request, 'Quiz updated successfully')
            return redirect('allQuizzes', code=code)

        return render(request, 'quiz/editQuiz.html', {'course': course, 'quiz': quiz, 'faculty': Faculty.objects.get(
            faculty_id=request.session['faculty_id'])})
    else:
        return redirect('std_login')


def deleteQuiz(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        if request.method == 'POST':
            # Delete the quiz
            quiz.delete()
            messages.success(request, 'Quiz deleted successfully')
            return redirect('allQuizzes', code=code)

        return render(request, 'quiz/deleteQuiz.html', {'quiz': quiz})
    else:
        return redirect('std_login')


def editQuestion(request, code, quiz_id, question_id):
    if is_faculty_authorised(request, code):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.question_set.all()

        if request.method == 'POST':
            for question in questions:
                question_id_str = str(question.id)

                # Retrieve values based on question type
                question_text = request.POST.get(f'question_{question_id_str}')
                marks = request.POST.get(f'marks_{question_id_str}')
                explanation = request.POST.get(f'explanation_{question_id_str}')

                if question.format == 'TF':
                    is_true = request.POST.get(f'is_true_{question_id_str}') == 'True'
                    question.is_true = is_true
                elif question.format == 'MCQ':
                    question.option1 = request.POST.get(f'option1_{question_id_str}')
                    question.option2 = request.POST.get(f'option2_{question_id_str}')
                    question.option3 = request.POST.get(f'option3_{question_id_str}')
                    question.option4 = request.POST.get(f'option4_{question_id_str}')
                    question.correct_answer = request.POST.get(f'correct_answer_{question_id_str}')
                elif question.format == 'FIB':
                    question.correct_answer = request.POST.get(f'correct_answer_fib_{question_id_str}')

                # Update common fields for all question types
                question.question = question_text
                question.marks = marks
                question.explanation = explanation

                question.save()

            messages.success(request, 'Questions updated successfully')
            return redirect('allQuizzes', code=code)

        return render(request, 'quiz/editQuestion.html', {'quiz': quiz, 'questions': questions})
    else:
        return redirect('std_login')