"""Small helpers for JSON endpoints."""
import json

from django.http import JsonResponse


def json_body(request):
    try:
        data = json.loads(request.body or b'{}')
        return data if isinstance(data, dict) else None
    except (ValueError, UnicodeDecodeError):
        return None


def bad(msg, status=400):
    return JsonResponse({'ok': False, 'error': msg}, status=status)
