from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.PositiveSmallIntegerField(choices=[(value, f'{value} star{"s" if value != 1 else ""}') for value in range(1, 6)])
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, blank=True, null=True, on_delete=models.SET_NULL, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'user'], name='unique_user_movie_rating'
            ),
            models.CheckConstraint(
                condition=models.Q(value__gte=1, value__lte=5),
                name='rating_value_between_1_and_5'
            ),
        ]

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - Review ' + str(self.review.id)