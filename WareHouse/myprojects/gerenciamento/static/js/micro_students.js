/* '''
JavaScript for the students microfrontend. Handles:
- loading lists of students, teachers, classes
- creating students
- assigning teacher to student
- assigning student to class
''' *quotes */
(async function() {
  // Clean handler via postMessage
  window.addEventListener('message', (event) => {
    if (event.data && event.data.action === 'clean') {
      if (studentsList) studentsList.innerHTML = '';
      if (studentSelectAssign) studentSelectAssign.innerHTML = '<option value="">-- select --</option>';
      if (studentSelectClass) studentSelectClass.innerHTML = '<option value="">-- select --</option>';
    }
  });
  // Helper to perform fetch with JSON
  async function api(path, opts = {}) {
    const res = await fetch(path, Object.assign({
      headers: {'Content-Type': 'application/json'}
    }, opts));
    return res;
  }
  // Elements
  const studentForm = document.getElementById('student-form');
  const studentsList = document.getElementById('students-list');
  const studentSelectAssign = document.getElementById('student-select-assign');
  const teacherSelectAssign = document.getElementById('teacher-select-assign');
  const assignTeacherForm = document.getElementById('assign-teacher-form');
  const studentSelectClass = document.getElementById('student-select-class');
  const classSelectAssign = document.getElementById('class-select-assign');
  const assignClassForm = document.getElementById('assign-class-form');
  // Load initial lists
  async function loadAll() {
    await Promise.all([loadStudents(), loadTeachers(), loadClasses()]);
  }
  async function loadStudents() {
    const res = await api('/api/students');
    const students = await res.json();
    // render list
    studentsList.innerHTML = '';
    studentSelectAssign.innerHTML = '<option value="">-- select --</option>';
    studentSelectClass.innerHTML = '<option value="">-- select --</option>';
    students.forEach(s => {
      const card = document.createElement('div');
      card.className = 'card';
      const teachers = (s.teachers && s.teachers.length) ? 'Teachers: ' + s.teachers.join(', ') : '';
      const classes = (s.classes && s.classes.length) ? 'Classes: ' + s.classes.join(', ') : '';
      card.innerHTML = `<strong>${s.name} (id:${s.id})</strong><br/><small>Age: ${s.age || '-'} · ${s.email || '-'}</small><div style="margin-top:6px;"><small>${teachers} ${classes}</small></div>`;
      studentsList.appendChild(card);
      // populate selects
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.name} (id:${s.id})`;
      studentSelectAssign.appendChild(opt);
      const opt2 = opt.cloneNode(true);
      studentSelectClass.appendChild(opt2);
    });
  }
  async function loadTeachers() {
    const res = await api('/api/teachers');
    const teachers = await res.json();
    if (teacherSelectAssign) {
      teacherSelectAssign.innerHTML = '<option value="">-- select --</option>';
    }
    const teacherSelectClassElem = document.getElementById('teacher-select-class');
    if (teacherSelectClassElem) {
      teacherSelectClassElem.innerHTML = '<option value="">-- select --</option>';
    }
    teachers.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = `${t.name} (id:${t.id})`;
      if (teacherSelectAssign) teacherSelectAssign.appendChild(opt);
      // Also update class-teacher select in top-level classes micro (if accessible)
      if (teacherSelectClassElem) {
        teacherSelectClassElem.appendChild(opt.cloneNode(true));
      }
    });
  }
  async function loadClasses() {
    const res = await api('/api/classes');
    const classes = await res.json();
    classSelectAssign.innerHTML = '<option value="">-- select --</option>';
    document.getElementById('class-select-assign').innerHTML = '<option value="">-- select --</option>';
    document.getElementById('class-select-teach')?.innerHTML && (document.getElementById('class-select-teach').innerHTML = '<option value="">-- select --</option>');
    classes.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `${c.name} (id:${c.id})`;
      classSelectAssign.appendChild(opt);
      // update other selects if present
      const other = document.getElementById('class-select-assign');
      if (other) other.appendChild(opt.cloneNode(true));
      const other2 = document.getElementById('class-select-teach');
      if (other2) other2.appendChild(opt.cloneNode(true));
    });
  }
  // Create student
  studentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = new FormData(studentForm);
    const payload = {
      name: form.get('name'),
      age: parseInt(form.get('age')) || 0,
      email: form.get('email')
    };
    const res = await api('/api/students', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      studentForm.reset();
      await loadAll();
      alert('Student registered');
    } else {
      const err = await res.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });
  // Assign teacher to student
  assignTeacherForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const student_id = parseInt(studentSelectAssign.value);
    const teacher_id = parseInt(teacherSelectAssign.value);
    if (!student_id || !teacher_id) {
      alert('Please select both student and teacher');
      return;
    }
    const res = await api('/api/assign_teacher_to_student', {
      method: 'POST',
      body: JSON.stringify({ student_id, teacher_id })
    });
    if (res.ok) {
      await loadAll();
      alert('Teacher assigned to student');
    } else {
      const err = await res.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });
  // Assign student to class
  assignClassForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const student_id = parseInt(studentSelectClass.value);
    const class_id = parseInt(classSelectAssign.value);
    if (!student_id || !class_id) {
      alert('Please select both student and class');
      return;
    }
    const res = await api('/api/assign_student_to_class', {
      method: 'POST',
      body: JSON.stringify({ student_id, class_id })
    });
    if (res.ok) {
      await loadAll();
      alert('Student assigned to class');
    } else {
      const err = await res.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });
  // Initial load
  await loadAll();
})();