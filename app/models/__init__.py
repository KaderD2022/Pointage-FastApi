# app/models/__init__.py
from .employee import Employee
from .attendance import Attendance
from .leave import Leave
from .holiday import Holiday
from .qrcode import GlobalQRCode  # Si vous avez ce fichier

__all__ = ['Employee', 'Attendance', 'Leave', 'Holiday', 'GlobalQRCode']