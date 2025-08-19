from datetime import datetime
from typing import List, Dict

def fetch_gregorian_holidays(year: int) -> List[Dict]:
    """Récupère les jours fériés du calendrier grégorien"""
    # Implémentation à compléter avec une API ou une liste statique
    holidays = [
        {"date": f"{year}-01-01", "name": "Nouvel An"},
        {"date": f"{year}-05-01", "name": "Fête du Travail"},
        # Ajouter tous les jours fériés
    ]
    return holidays

def is_holiday(date: str) -> bool:
    """Vérifie si une date est un jour férié"""
    # Implémentation à compléter
    return False