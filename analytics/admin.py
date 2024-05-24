from django.contrib import admin
from .models import AnalyticsOverview, AnalyticsCategory, AnalyticsTime

admin.site.register(AnalyticsOverview)
admin.site.register(AnalyticsCategory)
admin.site.register(AnalyticsTime)
