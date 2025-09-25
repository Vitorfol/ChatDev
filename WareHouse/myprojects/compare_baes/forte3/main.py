'''
Automated smoke test that exercises CRUD for Students, Courses, Enrollments, Teachers, Teachings.
This test uses the service layer directly (no HTTP). It assumes that migrations 1..6 have been applied.
It returns (ok: bool, details: str) to indicate pass/fail and diagnostic output.
This module was previously named main.py in early drafts and has been renamed to avoid conflicting
with the FastAPI application entrypoint. The test uses Pydantic domain input models so services
receive the expected types.
'''
import traceback
# Robust import: try package-style import (domain.entities) first, but fall back to a top-level
# entities.py import when the package path isn't present. This avoids ModuleNotFoundError
# when running this script directly in certain execution contexts.
try:
    from domain.entities import StudentIn, CourseIn, EnrollmentIn, TeacherIn, TeachingIn
except ModuleNotFoundError:
    from entities import StudentIn, CourseIn, EnrollmentIn, TeacherIn, TeachingIn
from services import StudentService, CourseService, EnrollmentService, TeacherService, TeachingService
from migrations import MigrationService
student_svc = StudentService()
course_svc = CourseService()
enrollment_svc = EnrollmentService()
teacher_svc = TeacherService()
teaching_svc = TeachingService()
migration_svc = MigrationService()
def run_smoke_test():
    details = []
    try:
        # Ensure all migrations applied (1..6)
        migration_svc.apply_up_to(6)
        details.append("Applied migrations up to 6.")
        # Students CRUD
        s = student_svc.create(StudentIn(id=None, email="alice@example.com"))
        sid = s["id"]
        details.append(f"Created student id={sid}")
        s2 = student_svc.get(sid)
        if not s2 or s2.get("email") != "alice@example.com":
            return False, "Student creation/read mismatch"
        details.append("Student read verified")
        student_svc.update(sid, StudentIn(email="alice2@example.com"))
        if student_svc.get(sid)["email"] != "alice2@example.com":
            return False, "Student update mismatch"
        details.append("Student update verified")
        # Courses CRUD
        c = course_svc.create(CourseIn(id=None, level="Undergrad"))
        cid = c["id"]
        details.append(f"Created course id={cid}")
        if course_svc.get(cid)["level"] != "Undergrad":
            return False, "Course creation/read mismatch"
        details.append("Course read verified")
        course_svc.update(cid, CourseIn(level="Grad"))
        if course_svc.get(cid)["level"] != "Grad":
            return False, "Course update mismatch"
        details.append("Course update verified")
        # Enrollment CRUD
        e = enrollment_svc.create(EnrollmentIn(student_id=sid, course_id=cid))
        eid = e["id"]
        details.append(f"Created enrollment id={eid}")
        if enrollment_svc.get(eid)["student_id"] != sid:
            return False, "Enrollment mismatch"
        details.append("Enrollment read verified")
        enrollment_svc.update(eid, EnrollmentIn(student_id=sid, course_id=cid))
        if enrollment_svc.get(eid)["course_id"] != cid:
            return False, "Enrollment update mismatch"
        details.append("Enrollment update verified")
        # Teachers CRUD
        t = teacher_svc.create(TeacherIn(id=None))
        tid = t["id"]
        details.append(f"Created teacher id={tid}")
        if not teacher_svc.get(tid):
            return False, "Teacher read mismatch"
        details.append("Teacher read verified")
        # Teaching CRUD
        teach = teaching_svc.create(TeachingIn(teacher_id=tid, course_id=cid))
        thid = teach["id"]
        details.append(f"Created teaching id={thid}")
        if teaching_svc.get(thid)["teacher_id"] != tid:
            return False, "Teaching mismatch"
        details.append("Teaching read verified")
        teaching_svc.update(thid, TeachingIn(teacher_id=tid, course_id=cid))
        if teaching_svc.get(thid)["course_id"] != cid:
            return False, "Teaching update mismatch"
        details.append("Teaching update verified")
        # Cleanup deletes
        teaching_svc.delete(thid)
        teacher_svc.delete(tid)
        enrollment_svc.delete(eid)
        course_svc.delete(cid)
        student_svc.delete(sid)
        details.append("Cleanup done")
        return True, "\n".join(details)
    except Exception as ex:
        tb = traceback.format_exc()
        return False, f"Exception during smoke test: {ex}\n{tb}"
if __name__ == "__main__":
    ok, det = run_smoke_test()
    print("SMOKE TEST OK:", ok)
    print(det)