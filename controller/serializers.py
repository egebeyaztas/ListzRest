from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model

from .models import Movie, Watchlist, Profile

User = get_user_model()

class UserPublicSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)

class ProfileSerializer(serializers.ModelSerializer):

    username = UserPublicSerializer(source='user', read_only=True)
    is_watched = serializers.SerializerMethodField(read_only=True)
    favourites = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username',
            'bio',
            'country',
            'is_watched',
            'favourites',
            'profile_picture'
        ]
    
    def get_is_watched(self, obj):
        return [watched_movie.title for watched_movie in obj.is_watched.all()]
    
    def get_favourites(self, obj):
        return [favourite.title for favourite in obj.favourites.all()]
    
    def get_profile_picture(self, obj):
        try:
            url_path =  obj.profile_picture.url
            return url_path
        except Exception as e:
            return 'Profile Picture not found..'

class MovieSerializer(serializers.ModelSerializer):

    edit_url = serializers.HyperlinkedIdentityField(view_name='rest_get_movie_details',
                                                    lookup_field='listz_id',
                                                    read_only=True)

    class Meta:
        model = Movie
        fields = [
            'title',
            'turkish_title',
            'imdb_id',
            'listz_id',
            'year',
            'imdb_rating',
            'genres',
            'certificate',
            'runtime',
            'countries',
            'directors',
            'stars',
            'plot',
            'poster_url',
            'edit_url',
        ]

    def get_edit_url(self, obj):
        request = self.context.get('request') # self.request
        if request is None:
            return None
        return reverse("rest_get_movie_details", kwargs={"listz_id": obj.listz_id}, request=request) 
    
class WatchlistSerializer(serializers.ModelSerializer):

    owner = UserPublicSerializer(source='user', read_only=True)
    followers = serializers.SerializerMethodField(read_only=True)
    movies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Watchlist
        fields = [
            'title',
            'owner',
            'followers',
            'movies',
        ]
    
    def get_owner(self, obj):
        return obj.profile.user.username
    
    def get_followers(self, obj):
        return [follower.user.username for follower in obj.followers.all()]
    
    def get_movies(self, obj):
        return [movie.title for movie in obj.movies.all()]