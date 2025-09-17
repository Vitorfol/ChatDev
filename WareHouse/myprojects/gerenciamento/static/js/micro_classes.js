
(async function() {
  // Clean handler via postMessage
  window.addEventListener('message', (event) => {
    if (event.data && event.data.action === 'clean') {
      if (classesList) classesList.innerHTML = '';
      if (classSelectTeach) classSelectTeach.innerHTML = '<option value="">-- select --</option>';
    }
  });
  async function api(path, opts = {}) {
    const res = await fetch(path, Object.assign({
      headers: {'Content-Type': 'application/json'}
    }, opts));
    return res;
  }
  const classForm = document.getElementById('class-form');
  const classesList = document.getElementById('classes-list');
  const teacherSelectClass = document.getElementById('teacher-select-class');
  const classSelectTeach = document.getElementById('class-select-teach');
  const assignTeacherClassForm = document.getElementById('assign-teacher-class-form');
  async function loadAll() {
    await Promise.all([loadClasses(), loadTeachers()]);
  }
  async function loadClasses() {
    const res = await api('/api/classes');
    const classes = await res.json();
    classesList.innerHTML = '';
    classSelectTeach.innerHTML = '<option value="">-- select --</option>';
    document.getElementById('class-select-assign') && (document.getElementById('class-select-assign').innerHTML = '<option value="">-- select --</option>');
    classes.forEach(c => {
      const card = document.createElement('div');
      card.className = 'card';
      const schedule = (c.schedule && c.schedule.length) ? c.schedule.map(s => s.day + ' ' + s.time).join(' · ') : '-';
      card.innerHTML = `<strong>${c.name} (id:${c.id})</strong><br/><small>Teacher: ${c.teacher_id || '-'}</small><div style="margin-top:6px;"><small>Schedule: ${schedule}</small></div>`;
      classesList.appendChild(card);
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `${c.name} (id:${c.id})`;
      classSelectTeach.appendChild(opt);
      // Also update other selects
      const other = document.getElementById('class-select-assign');
      if (other) other.appendChild(opt.cloneNode(true));
      const other2 = document.getElementById('class-select-teach');
      if (other2) {
        // handled earlier
      }
    });
  }
  async function loadTeachers() {
    const res = await api('/api/teachers');
    const teachers = await res.json();
    teacherSelectClass.innerHTML = '<option value="">-- select --</option>';
    document.getElementById('teacher-select-assign') && (document.getElementById('teacher-select-assign').innerHTML = '<option value="">-- select --</option>');
    teachers.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = `${t.name} (id:${t.id})`;
      teacherSelectClass.appendChild(opt);
      const other = document.getElementById('teacher-select-assign');
      if (other) other.appendChild(opt.cloneNode(true));
    });
  }
  classForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = new FormData(classForm);
    const scheduleRaw = form.get('schedule') || '';
    const schedule = scheduleRaw.split(',').map(s => s.trim()).filter(Boolean).map(item => {
      // Try to split "Day time" naive
      const parts = item.split(/\s+(.+)/); // split into day and rest
      if (parts.length >= 2) {
        return { day: parts[0], time: parts[1] };
      } else {
        return { day: '', time: item };
      }
    });
    const payload = {
      name: form.get('name'),
      schedule: schedule
    };
    const res = await api('/api/classes', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      classForm.reset();
      await loadAll();
      alert('Class created');
    } else {
      const err = await res.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });
  assignTeacherClassForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const teacher_id = parseInt(teacherSelectClass.value);
    const class_id = parseInt(classSelectTeach.value);
    if (!teacher_id || !class_id) {
      alert('Please select both teacher and class');
      return;
    }
    const res = await api('/api/assign_teacher_to_class', {
      method: 'POST',
      body: JSON.stringify({ teacher_id, class_id })
    });
    if (res.ok) {
      await loadAll();
      alert('Teacher assigned to class');
    } else {
      const err = await res.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });
  await loadAll();
})();