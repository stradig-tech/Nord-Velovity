from django.contrib import admin
from .models import PageView, BookingFunnelEvent, SearchQueryLog

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'user', 'ip_address', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('path', 'ip_address', 'user__email')
    readonly_fields = ('path', 'user', 'ip_address', 'user_agent', 'referrer', 'timestamp')

    def has_add_permission(self, request):
        return False

@admin.register(BookingFunnelEvent)
class BookingFunnelEventAdmin(admin.ModelAdmin):
    list_display = ('stage', 'tour', 'user', 'session_key', 'timestamp')
    list_filter = ('stage', 'timestamp')
    search_fields = ('session_key', 'user__email', 'tour__title')
    readonly_fields = ('stage', 'session_key', 'user', 'tour', 'metadata', 'timestamp')

    def has_add_permission(self, request):
        return False

@admin.register(SearchQueryLog)
class SearchQueryLogAdmin(admin.ModelAdmin):
    list_display = ('query', 'destination', 'results_count', 'user', 'timestamp')
    list_filter = ('destination', 'timestamp')
    search_fields = ('query', 'user__email', 'ip_address')
    readonly_fields = ('query', 'destination', 'results_count', 'user', 'ip_address', 'timestamp')

    def has_add_permission(self, request):
        return False

