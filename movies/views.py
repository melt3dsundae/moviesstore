from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count
from django.db import transaction
from .forms import FeedbackForm
from .models import Movie, Review, Report, Rating
from django.contrib.auth.decorators import login_required
# https://docs.djangoproject.com/en/1.8/intro/tutorial02/
# https://docs.djangoproject.com/en/6.1/topics/db/transactions/

def _movie_detail_data(movie, user, feedback_form=None):
    reviews = Review.objects.filter(movie=movie).select_related('user').prefetch_related('ratings')
    ratings = Rating.objects.filter(movie=movie)
    rating_summary = ratings.aggregate(average=Avg('value'), count=Count('id'))
    user_rating = ratings.filter(user=user).first() if user.is_authenticated else None
    return {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews,
        'average_rating': rating_summary['average'],
        'rating_count': rating_summary['count'],
        'user_rating': user_rating,
        'feedback_form': feedback_form or FeedbackForm(
            initial={'rating': user_rating.value if user_rating else None}
        ),
    }

# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = get_object_or_404(Movie, id=id)
    template_data = _movie_detail_data(movie, request.user)
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    movie = get_object_or_404(Movie, id=id)
    if request.method != 'POST':
        return redirect('movies.show', id=id)
    form = FeedbackForm(request.POST)
    if not form.is_valid():
        template_data = _movie_detail_data(movie, request.user, form)
        return render(request, 'movies/show.html', {'template_data': template_data}, status=400)
    with transaction.atomic():
        comment = form.cleaned_data['comment']
        review = None
        if comment:
            review = Review.objects.create(
                comment=comment,
                movie=movie,
                user=request.user,
            )
        value = form.cleaned_data['rating']
        if value is not None:
            rating, created = Rating.objects.get_or_create(
                movie=movie,
                user=request.user,
                defaults={'value': value, 'review': review},
            )
            if not created:
                rating.value = value
                update_fields = ['value']
                if review:
                    rating.review = review
                    update_fields.append('review')
                rating.save(update_fields=update_fields)
    return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def create_report(request, id, review_id):
    movie = Movie.objects.get(id=id)
    review = Review.objects.get(id=review_id)
    report = Report()
    report.movie = movie
    report.user = request.user
    report.review = review
    report.save()
    return redirect('movies.show', id=id)