from app.forms.auth_forms import (
    LoginForm, ChangePasswordForm, UserForm, RoleForm, UserRoleForm
)
from app.forms.academic_forms import (
    CampusForm, FacultyForm, DepartmentForm, ProgramForm, AcademicYearForm, SemesterForm, CourseForm, CoursePrerequisiteForm
)
from app.forms.student_forms import (
    StudentForm, InstructorForm, StaffForm, GuardianForm, StudentGuardianForm
)
from app.forms.enrollment_forms import (
    ClassroomForm, CourseSectionForm, SectionScheduleForm, EnrollmentForm, AttendanceForm
)
from app.forms.exam_forms import (
    AssessmentForm, AssessmentResultForm, ExamForm, ExamRoomForm, ExamSeatingForm, GradeForm, TranscriptForm
)
from app.forms.finance_forms import (
    FeeTypeForm, FeeStructureForm, StudentInvoiceForm, InvoiceItemForm, PaymentForm, ScholarshipForm, ScholarshipAwardForm
)
from app.forms.service_forms import (
    LibraryBookForm, BookCopyForm, LibraryLoanForm, LibraryFineForm,
    HostelBuildingForm, HostelRoomForm, HostelAllocationForm,
    TransportRouteForm, TransportVehicleForm, TransportAssignmentForm,
    AnnouncementForm, NotificationForm, AuditLogForm
)
