'''
Main entrypoint for the simple school management microfrontend app.
This file starts a Flask web server that serves a "shell" page and three
microfrontend pages (students, teachers, classes). It provides REST API
endpoints for creating/listing students, teachers, classes and for creating
relationships (assigning teachers to students, and assigning students/teachers
to classes). Data is persisted to a simple JSON file via storage.py.
'''
from flask import Flask, jsonify, request, render_template, send_from_directory
from models import Student, Teacher, ClassRoom
from storage import Storage
import os
app = Flask(__name__, static_folder='static', template_folder='templates')
DB_FILE = 'data/db.json'
# Ensure data directory exists before instantiating Storage to avoid FileNotFoundError
dirpath = os.path.dirname(DB_FILE)
if dirpath:
    os.makedirs(dirpath, exist_ok=True)
storage = Storage(DB_FILE)
# Ensure DB exists and is initialized
storage.ensure_initialized()
@app.route('/')
def shell():
    """
    Render the shell page which uses iframes to load microfrontends.
    """
    return render_template('index.html')
@app.route('/micro/students')
def micro_students():
    return render_template('micro_students.html')
@app.route('/micro/teachers')
def micro_teachers():
    return render_template('micro_teachers.html')
@app.route('/micro/classes')
def micro_classes():
    return render_template('micro_classes.html')
# API endpoints for Students
@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    if request.method == 'GET':
        students = storage.get_all_students()
        return jsonify(students)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    student = Student.from_dict(data)
    created = storage.create_student(student)
    return jsonify(created), 201
# API endpoints for Teachers
@app.route('/api/teachers', methods=['GET', 'POST'])
def api_teachers():
    if request.method == 'GET':
        teachers = storage.get_all_teachers()
        return jsonify(teachers)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    teacher = Teacher.from_dict(data)
    created = storage.create_teacher(teacher)
    return jsonify(created), 201
# API endpoints for Classes
@app.route('/api/classes', methods=['GET', 'POST'])
def api_classes():
    if request.method == 'GET':
        classes = storage.get_all_classes()
        return jsonify(classes)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    classroom = ClassRoom.from_dict(data)
    created = storage.create_class(classroom)
    return jsonify(created), 201
# Relationship endpoints
@app.route('/api/assign_teacher_to_student', methods=['POST'])
def api_assign_teacher_to_student():
    data = request.get_json()
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')
    if student_id is None or teacher_id is None:
        return jsonify({'error': 'student_id and teacher_id required'}), 400
    success, msg = storage.assign_teacher_to_student(student_id, teacher_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg})
@app.route('/api/assign_student_to_class', methods=['POST'])
def api_assign_student_to_class():
    data = request.get_json()
    student_id = data.get('student_id')
    class_id = data.get('class_id')
    if student_id is None or class_id is None:
        return jsonify({'error': 'student_id and class_id required'}), 400
    success, msg = storage.assign_student_to_class(student_id, class_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg})
@app.route('/api/assign_teacher_to_class', methods=['POST'])
def api_assign_teacher_to_class():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    class_id = data.get('class_id')
    if teacher_id is None or class_id is None:
        return jsonify({'error': 'teacher_id and class_id required'}), 400
    success, msg = storage.assign_teacher_to_class(teacher_id, class_id)
    if not success:
        return jsonify({'error': msg}), 400
    return jsonify({'message': msg})
# Serve static files (CSS/JS) explicitly for clarity
@app.route('/api/clean_all', methods=['POST'])
def api_clean_all():
    storage.clear_all()
    return jsonify({'message': 'Banco de dados limpo com sucesso!'}), 200
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
if __name__ == '__main__':
    # Create data directory if needed (redundant but defensive)
    os.makedirs('data', exist_ok=True)
    print("Starting School Management Microfrontend App on http://127.0.0.1:5000")
    app.run(debug=True)