# app/utils/reports.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from io import BytesIO
from datetime import datetime
from typing import List, Dict
import pandas as pd

def generate_employees_report_pdf(employees_data: List[Dict], start_date: str, end_date: str) -> BytesIO:
    """Génère un PDF avec la liste des employés et leurs statistiques"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Titre
    title = Paragraph("RAPPORT DES EMPLOYÉS", styles['Title'])
    elements.append(title)
    
    # Période
    period_text = Paragraph(f"Période: {start_date} au {end_date}", styles['Normal'])
    elements.append(period_text)
    
    # Date de génération
    gen_date = Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
    elements.append(gen_date)
    
    elements.append(Spacer(1, 20))
    
    # Tableau des employés
    if employees_data:
        table_data = [
            ["ID", "Nom", "Prénom", "Présence", "Retards", "Absences", "Heures"]
        ]
        
        for emp in employees_data:
            stats = emp.get('stats', {})
            table_data.append([
                str(emp.get('id', '')),
                emp.get('last_name', ''),
                emp.get('first_name', ''),
                str(stats.get('present_days', 0)),
                str(stats.get('late_days', 0)),
                str(stats.get('absent_days', 0)),
                str(stats.get('worked_hours', 0))
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun employé trouvé.", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_attendance_report_pdf(attendance_data: List[Dict], employee_name: str = None) -> BytesIO:
    """Génère un PDF avec les pointages"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Titre
    title = "RAPPORT DES POINTAGES"
    if employee_name:
        title += f" - {employee_name}"
    elements.append(Paragraph(title, styles['Title']))
    
    elements.append(Spacer(1, 20))
    
    # Tableau des pointages
    if attendance_data:
        table_data = [["Date", "Arrivée matin", "Départ matin", "Arrivée aprèm", "Départ aprèm", "Statut"]]
        
        for att in attendance_data:
            table_data.append([
                att.get('date', ''),
                att.get('morning_arrival', '-'),
                att.get('morning_departure', '-'),
                att.get('afternoon_arrival', '-'),
                att.get('afternoon_departure', '-'),
                get_attendance_status(att)
            ])
        
        table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun pointage trouvé.", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_leaves_report_pdf(leaves_data: List[Dict]) -> BytesIO:
    """Génère un PDF avec la liste des congés"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("RAPPORT DES CONGÉS ET PERMISSIONS", styles['Title']))
    elements.append(Spacer(1, 20))
    
    if leaves_data:
        table_data = [["Employé", "Type", "Début", "Fin", "Statut", "Raison"]]
        
        for leave in leaves_data:
            table_data.append([
                f"{leave.get('employee_last_name', '')} {leave.get('employee_first_name', '')}",
                leave.get('leave_type', ''),
                leave.get('start_date', ''),
                leave.get('end_date', ''),
                leave.get('status', ''),
                leave.get('reason', '') or '-'
            ])
        
        table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Aucun congé trouvé.", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_stats_report_pdf(stats_data: Dict) -> BytesIO:
    """Génère un PDF avec les statistiques"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("RAPPORT STATISTIQUES", styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Tableau des statistiques
    table_data = [
        ["Statistique", "Valeur", "Pourcentage"],
        ["Employés totaux", str(stats_data.get('total_employees', 0)), "100%"],
        ["Employés à l'heure", str(stats_data.get('on_time_employees', 0)), f"{stats_data.get('percentages', {}).get('on_time', 0)}%"],
        ["Employés en retard", str(stats_data.get('late_employees', 0)), f"{stats_data.get('percentages', {}).get('late', 0)}%"],
        ["Congés totaux", str(stats_data.get('total_leaves', 0)), "-"],
        ["Jours fériés", str(stats_data.get('holidays', 0)), "-"]
    ]
    
    table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_global_qr_pdf(qr_data: str, qr_type: str) -> BytesIO:
    """Génère un PDF avec le QR code global"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    elements = []
    
    title = f"QR CODE {qr_type.upper()}"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 40))
    
    # Ici vous devrez ajouter la logique pour insérer l'image du QR code
    # Pour l'instant, on affiche juste les données textuelles
    elements.append(Paragraph(f"Données QR: {qr_data}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def get_attendance_status(attendance: Dict) -> str:
    """Retourne le statut du pointage"""
    if attendance.get('is_holiday'):
        return "Férié"
    if attendance.get('is_on_leave'):
        return "Congé"
    if attendance.get('is_absent'):
        return "Absent"
    if attendance.get('is_late_morning') or attendance.get('is_late_afternoon'):
        return "Retard"
    return "Présent"