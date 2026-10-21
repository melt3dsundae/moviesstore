from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.urls import path

# Register your models here.
from .models import Movie, Rating, Review, Report

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

    change_list_template = 'admin/movies/movie/change_list.html'

    def get_urls(self):
        return [
            path(
                'statistics/',
                self.admin_site.admin_view(self.statistics_view),
                name='movies_movie_statistics'
            ),
            path(
                'user-statistics/',
                self.admin_site.admin_view(self.user_statistics_view),
                name='movies_movie_user_statistics'
            ),
        ] + super().get_urls()
    
    def statistics_view(self, request):
        most_reviewed = (
            Movie.objects
            .annotate(review_count=Count('review'))
            .filter(review_count__gt=0)
            .order_by('-review_count', 'name', 'pk')
            .first()
        )
        most_purchased = (
            Movie.objects
            .annotate(purchase_count=Sum('item__quantity'))
            .filter(purchase_count__gt=0)
            .order_by('-purchase_count', 'name', 'pk')
            .first()
        )

        context = {
            **self.admin_site.each_context(request),
            'title': 'Movie Statistics',
            'most_reviewed': most_reviewed,
            'most_purchased': most_purchased
        }

        return TemplateResponse(
            request,
            'admin/movies/movie/statistics.html',
            context
        )
    
    def user_statistics_view(self, request):
        most_comments = (
            User.objects
            .annotate(comment_count=Count('review'))
            .filter(comment_count__gt=0)
            .order_by('-comment_count', 'username', 'pk')
            .first()
        )

        context = {
            **self.admin_site.each_context(request),
            'title': 'User Comment Statistics',
            'most_comments': most_comments
        }

        return TemplateResponse(
            request,
            'admin/movies/movie/user_statistics.html',
            context
        )


admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Rating)
admin.site.register(Report)