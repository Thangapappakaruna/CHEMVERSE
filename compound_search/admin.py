from django.contrib import admin

from .models import ChemicalProperty, Compound, FavoriteCompound, SearchHistory


class PropertyInline(admin.TabularInline):
    model = ChemicalProperty
    extra = 0


@admin.register(Compound)
class CompoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'formula', 'molar_mass', 'melting_point', 'boiling_point', 'state', 'data_quality')
    list_filter = ('state', 'category', 'data_quality')
    search_fields = ('name', 'formula')
    inlines = [PropertyInline]


admin.site.register(FavoriteCompound)
admin.site.register(SearchHistory)
