/* '''
JavaScript for the teachers microfrontend. Handles:
- loading and rendering teachers list
- creating teachers (POST /api/teachers)
''' *quotes */
(async function() {
  // Clean handler via postMessage
  window.addEventListener('message', (event) => {
    if (event.data && event.data.action === 'clean') {
      if (teachersList) teachersList.innerHTML = '';
    }
  });
  async function api(path, opts = {}) {
    const res = await fetch(path, Object.assign({
      headers: {'Content-Type': 'application/json'}
    }, opts));
    return res;
  }
  const teacherForm = document.getElementById('teacher-form');
  const teachersList = document.getElementById('teachers-list');
  async function loadTeachers() {
    const res = await api('/api/teachers');
    const teachers = await res.json();
    teachersList.innerHTML = '';
    teachers.forEach(t => {
      const card = document.createElement('div');
      card.className = 'card';
      const students = (t.students && t.students.length) ? 'Students: ' + t.students.join(', ') : '';
      card.innerHTML = `<strong>${t.name} (id:${t.id})</strong><br/><small>Subject: ${t.subject || '-'} · ${t.email || '-'}</small><div style="margin-top:6px;"><small>${students}</small></div>`;
      teachersList.appendChild(card);
    });
    // Also post a message to parent to let other microfrontends refresh selects via shell (optional)
  }
  teacherForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = new FormData(teacherForm);
    const payload = {
      name: form.get('name'),
      subject: form.get('subject'),
      email: form.get('email')
    };
    const res = await api('/api/teachers', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      teacherForm.reset();
      await loadTeachers();
      alert('Teacher registered');
    } else {
      const err = await res.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });
  await loadTeachers();
})();