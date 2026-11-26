"""Records which tools a signed-in user opens, for 'Recently visited tools' on the dashboard."""
from . import guest
from .utils import log_activity, recent_visit_exists

TOOLS = [
    ('/learn/', 'Chemistry Lessons'), ('/periodic-table/', 'Periodic Table'), ('/compounds/', 'Compound Search'),
    ('/boiling-melting/', 'Boiling & Melting Points'), ('/structure-lab/', 'Structure Lab'),
    ('/reactions/', 'Reaction Builder'), ('/balancer/', 'Equation Balancer'), ('/games/', 'Chemistry Games'),
    ('/quiz/', 'Chemistry Quiz'), ('/molecular-weight/', 'Molecular Weight'), ('/lab/', 'Lab Simulator'),
    ('/dictionary/', 'Chemistry Dictionary'), ('/community/', 'Community'),
]


class ActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if request.method == 'GET' and response.status_code == 200 and '/api/' not in request.path:
                for prefix, label in TOOLS:
                    if request.path.startswith(prefix):
                        if request.user.is_authenticated:
                            if not recent_visit_exists(request.user, label):
                                log_activity(request.user, 'visit', label, prefix)
                        elif hasattr(request, 'session'):
                            guest.visit(request, label, prefix)
                        break
        except Exception:  # activity logging must never break a page
            pass
        return response
