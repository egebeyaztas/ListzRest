from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.core import files
from django.core.exceptions import ValidationError
from django_extensions.db.fields import AutoSlugField
from io import BytesIO
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField
from scripts.keygen import KeyGenerator

keygenerator = KeyGenerator()

class Movie(models.Model):
	title = models.CharField(max_length=300)
	turkish_title = models.CharField(max_length=300)
	imdb_id = models.CharField(max_length=20, blank=True)
	listz_id = models.CharField(max_length=25, default=keygenerator.generate_unique_key)
	year = models.CharField(max_length=25, blank=True)
	imdb_rating = models.CharField(max_length=10, blank=True)
	certificate = models.CharField(max_length=10, blank=True)
	runtime = models.CharField(max_length=25, blank=True)
	genres = ArrayField(models.CharField(max_length=50), blank=True)
	director = models.CharField(max_length=120, blank=True)
	stars = ArrayField(models.CharField(max_length=50), blank=True)
	country = models.CharField(max_length=50, blank=True)
	plot = models.TextField(max_length=500, blank=True)
	poster_url = models.URLField(blank=True, max_length=500)
	votes = models.CharField(max_length=12, blank=True)
	keywords = ArrayField(models.CharField(max_length=100), blank=True)
	slug = AutoSlugField(populate_from=['title', 'year'])
	vector_column = SearchVectorField(null=True)


	class Meta:
		indexes = [
			GinIndex(fields=['vector_column']),
		]
		ordering = ('id',)

	def __str__(self):
		return self.title

	def avg_rating(self):
		if len(self.rating_set.all()) > 0:
			all_rates = self.rating_set.all().values_list('rate', flat=True)
			return sum(all_rates)/len(all_rates)


def user_path(instance, filename):
    if instance.user:
        return f'profile_pictures/{instance.user.username}/{filename}'
    return f'profile_pictures/{instance.user}/{filename}'

class Profile(models.Model):
    
    user = models.OneToOneField(User,unique=True, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True)
    bio = models.TextField(blank=True, max_length=255)
    profile_picture = models.ImageField(default="", upload_to=user_path, blank=True)
    is_watched = models.ManyToManyField(Movie, related_name='watched_by', blank=True)
    favourites = models.ManyToManyField(Movie, related_name='faved_by', blank=True)
    rated_movies = models.ManyToManyField(Movie, related_name='rated_users', through='Rating', blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    @property
    def image_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url

    def __str__(self):
        if self.user:
            return str(self.user.username)
        return str(self.user)
    
    '''This function allows users to rate movies only once.'''
    def rate_movie(self, movie: 'Movie', rate: int):
        if not movie in self.rated_movies.all():
            rating = Rating(user=self, movie=movie, rate=rate)
            rating.save()

    '''Following the given watchlist'''
    def follow_watchlist(self, watch_list):
        if self.user != watch_list.user:
            if not watch_list in self.following_watchlists.all():
                self.following_watchlists.add(watch_list)
                self.save()
        else:
            raise Exception("You cannot follow your own watchlist")

    '''Unfollowing the given watchlist'''
    def unfollow_watchlist(self, watch_list):
        if watch_list in self.following_watchlists.all():
            self.following_watchlists.remove(watch_list)
            watch_list.followers.remove(self)

    '''Adding movies to the User's favourite table'''
    def add_to_favs(self, movie: Movie):
        if not movie in self.favourites.all():
            self.favourites.add(movie)
            self.save()

    '''Removing movies from favs'''
    def remove_from_favs(self, movie: Movie):
        if movie in self.favourites.all():
            self.favourites.remove(movie)

    '''Add the movies that you watched to the 
                    table of watched movies'''
    def movie_is_watched(self, movie: Movie):
        if not movie in self.is_watched.all():
            self.is_watched.add(movie)
            self.save()
    
    '''Remove the movies that you watched to the 
                        table of watched movies'''
    def movie_unwatched(self, movie: Movie):
        if movie in self.is_watched.all():
            self.is_watched.remove(movie)

    '''Add movies to your watchlists'''
    def add_to_watchlist(self, movie: Movie, watchlist):
        if self.watchlists.exists():
            if watchlist in self.watchlists.all():
                if not movie in watchlist.movies.all():
                    watchlist.add(movie)
                    watchlist.save()            

    '''Remove movies from your watchlists'''
    def remove_from_watchlist(self, movie: Movie, watchlist):
        if self.watchlists.exists():
            if watchlist in self.watchlists.all():
                if movie in watchlist.movies.all():
                    watchlist.remove(movie)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        #group = Group.objects.get(name="users")
        #instance.groups.add(group)
        Profile.objects.create(user=instance)
        print(f'profile created for {instance.username}')


class Watchlist(models.Model):
    title = models.CharField(max_length=40, blank=False)
    profile = models.ForeignKey(Profile, related_name="watchlists", on_delete=models.CASCADE)
    followers = models.ManyToManyField(Profile, related_name='following_watchlists', blank=True)
    movies = models.ManyToManyField(Movie, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    slug = AutoSlugField(populate_from=['profile__user__username','title'], unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('list-to-grid-view', args=[str(self.slug)])

    def __str__(self):
        return str(self.title)

def max_movies_added(sender, **kwargs):
    if kwargs['instance'].movies.count() > 25:
        raise ValidationError('You can only assign 25 movies to a single watchlist.')

m2m_changed.connect(max_movies_added, sender=Watchlist.movies.through)


class Rating(models.Model):
    CHOICES = (
        (1,1),(2,2),(3,3),(4,4),(5,5),
        (6,6),(7,7),(8,8),(9,9),(10,10)
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rate = models.IntegerField(choices=CHOICES, default=0)

    def __str__(self):
        return str(self.rate)
