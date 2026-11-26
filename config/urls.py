from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('learn/', include('chemistry_learning.urls')),
    path('periodic-table/', include('periodic_table.urls')),
    path('compounds/', include('compound_search.urls')),
    path('boiling-melting/', include('boiling_melting.urls')),
    path('structure-lab/', include('molecular_structure.urls')),
    path('reactions/', include('reaction_builder.urls')),
    path('balancer/', include('reaction_balancer.urls')),
    path('games/', include('chemistry_games.urls')),
    path('quiz/', include('chemistry_quiz.urls')),
    path('molecular-weight/', include('molecular_weight.urls')),
    path('lab/', include('lab_simulator.urls')),
    path('dictionary/', include('chemistry_dictionary.urls')),
    path('community/', include('community.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'dashboard.views.error_404'
handler500 = 'dashboard.views.error_500'
