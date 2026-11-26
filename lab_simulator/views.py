from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from accounts.utils import add_xp
from config.http import bad, json_body
from dashboard import guest
from dashboard.utils import log_activity

from .models import Experiment, ExperimentLog


def index(request):
    if request.user.is_authenticated:
        logs = [{'title': l.experiment.title, 'result': l.result, 'when': l.created_at} for l in
                ExperimentLog.objects.filter(user=request.user).select_related('experiment')[:8]]
    else:
        logs = [{'title': e['title'], 'result': e['result'], 'when': None} for e in guest.summary(request)['experiments'][:8]]
    return render(request, 'lab_simulator/index.html', {'experiments': Experiment.objects.all(), 'logs': logs})


def experiment(request, slug):
    exp = get_object_or_404(Experiment, slug=slug)
    template = f'lab_simulator/exp_{slug.replace("-", "_")}.html'
    logs = ExperimentLog.objects.filter(user=request.user, experiment=exp)[:5] if request.user.is_authenticated else []
    return render(request, template, {'exp': exp, 'logs': logs})


@require_POST
def record(request, slug):
    exp = get_object_or_404(Experiment, slug=slug)
    data = json_body(request)
    if data is None:
        return bad('Invalid JSON')
    result = str(data.get('result', '')).strip()[:250]
    if not result:
        return bad('Nothing to record')
    if not request.user.is_authenticated:
        guest.add_experiment(request, exp.title, result)
        return JsonResponse({'ok': True, 'guest': True})
    ExperimentLog.objects.create(user=request.user, experiment=exp, result=result)
    if ExperimentLog.objects.filter(user=request.user, experiment=exp).count() == 1:
        add_xp(request.user, 15)
    log_activity(request.user, 'experiment', f'{exp.title}: {result}', f'/lab/{exp.slug}/')
    return JsonResponse({'ok': True})
