from app.models.auth import (
    User, Role, UserRole, Student, Instructor, Staff, Guardian, StudentGuardian
)
from app.models.academic import (
    Campus, Faculty, Department, Program, AcademicYear, Semester, Course, CoursePrerequisite
)
from app.models.enrollment import (
    Classroom, CourseSection, SectionSchedule, Enrollment, Attendance
)
from app.models.examination import (
    Assessment, AssessmentResult, Exam, ExamRoom, ExamSeating, Grade, Transcript
)
from app.models.finance import (
    FeeType, FeeStructure, StudentInvoice, InvoiceItem, Payment, Scholarship, ScholarshipAward
)
from app.models.library import (
    LibraryBook, BookCopy, LibraryLoan, LibraryFine
)
from app.models.hostel import (
    HostelBuilding, HostelRoom, HostelAllocation
)
from app.models.transport import (
    TransportRoute, TransportVehicle, TransportAssignment
)
from app.models.system import (
    Announcement, Notification, AuditLog
)

ALL_MODELS = [
    # Module A: Authentication & User Management (8)
    User, Role, UserRole, Student, Instructor, Staff, Guardian, StudentGuardian,
    # Module B: Academic Management (8)
    Campus, Faculty, Department, Program, AcademicYear, Semester, Course, CoursePrerequisite,
    # Module C: Classes and Enrollment (5)
    Classroom, CourseSection, SectionSchedule, Enrollment, Attendance,
    # Module D: Examination and Results (7)
    Assessment, AssessmentResult, Exam, ExamRoom, ExamSeating, Grade, Transcript,
    # Module E: Finance and Fee Management (7)
    FeeType, FeeStructure, StudentInvoice, InvoiceItem, Payment, Scholarship, ScholarshipAward,
    # Module F: Library Management (4)
    LibraryBook, BookCopy, LibraryLoan, LibraryFine,
    # Module G: Hostel Management (3)
    HostelBuilding, HostelRoom, HostelAllocation,
    # Module H: Transport Management (3)
    TransportRoute, TransportVehicle, TransportAssignment,
    # Module I: Notifications and System (3)
    Announcement, Notification, AuditLog
]

__all__ = [
    'User', 'Role', 'UserRole', 'Student', 'Instructor', 'Staff', 'Guardian', 'StudentGuardian',
    'Campus', 'Faculty', 'Department', 'Program', 'AcademicYear', 'Semester', 'Course', 'CoursePrerequisite',
    'Classroom', 'CourseSection', 'SectionSchedule', 'Enrollment', 'Attendance',
    'Assessment', 'AssessmentResult', 'Exam', 'ExamRoom', 'ExamSeating', 'Grade', 'Transcript',
    'FeeType', 'FeeStructure', 'StudentInvoice', 'InvoiceItem', 'Payment', 'Scholarship', 'ScholarshipAward',
    'LibraryBook', 'BookCopy', 'LibraryLoan', 'LibraryFine',
    'HostelBuilding', 'HostelRoom', 'HostelAllocation',
    'TransportRoute', 'TransportVehicle', 'TransportAssignment',
    'Announcement', 'Notification', 'AuditLog',
    'ALL_MODELS'
]
