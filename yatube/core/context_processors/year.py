from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = datetime.now()
    return {
        'year': int(current_date.year)
    }
