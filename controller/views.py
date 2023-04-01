from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Movie, Watchlist, Profile
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import MovieSerializer, WatchlistSerializer, ProfileSerializer
from .mixins import StaffEditorPermissionMixin, UserQuerySetMixin

@api_view(['GET'])
def api_home(request):
    if request.method == 'GET':
        data = {'Welcome to': 'Listz Movie API!'}
        return Response(data)
    
"""
@api_view(['GET'])
def get_movie_list(request, pk=None, *args, **kwargs):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    if request.method == 'GET':
        qs = Movie.objects.all().order_by('id').prefetch_related('actors') #actors deprecated
        qs_paginated = paginator.paginate_queryset(qs, request)            # for public repo
        data = MovieSerializer(qs_paginated, many=True, context={'request': request})
        return paginator.get_paginated_response(data.data)

@api_view(['GET'])
def get_movie_details(request, pk, *args, **kwargs):
    if pk is not None:
            movie = get_object_or_404(Movie, pk=pk)
            data = MovieSerializer(movie, many=False, context={'request': request}).data
            return Response(data)
"""
#  ---------------------- Implementation -------------------------- 

#Movie CRUD Operations
#ListView
class MovieListAPIView(generics.ListAPIView,
                       StaffEditorPermissionMixin):
     
     permission_classes = (IsAuthenticated,)
     queryset = Movie.objects.all().order_by('id')
     serializer_class = MovieSerializer

movie_list_api_view = MovieListAPIView.as_view()

#DetailView
class MovieDetailAPIView(generics.RetrieveAPIView,
                         StaffEditorPermissionMixin):
    
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer
    lookup_field = 'listz_id'

movie_detail_api_view = MovieDetailAPIView.as_view()

#CreateView
class MovieCreateAPIView(generics.CreateAPIView,
                         StaffEditorPermissionMixin):
    
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer

movie_create_api_view = MovieCreateAPIView.as_view()

#UpdateView
class MovieUpdateAPIView(generics.UpdateAPIView,
                         StaffEditorPermissionMixin):
    
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer
    lookup_field = 'pk'

movie_update_api_view = MovieUpdateAPIView.as_view()

#DeleteView
class MovieDeleteAPIView(generics.DestroyAPIView,
                         StaffEditorPermissionMixin):
    
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

movie_delete_api_view = MovieDeleteAPIView.as_view()

#  WATCHLIST REST Operations

#ListView
class WatchListAPIView(generics.ListAPIView):
    queryset = Watchlist.objects.all().order_by('-pk')
    serializer_class = WatchlistSerializer

watchlists_api_view = WatchListAPIView.as_view()

#User Specific List View
class UserWatchlistsAPIView(generics.ListAPIView,
                            UserQuerySetMixin):
    queryset = Watchlist.objects.all().order_by('-pk')
    serializer_class = WatchlistSerializer
    lookup_field = 'user'

    def get(self, request, *args, **kwargs):
        user = request.user
        qs = Watchlist.objects.filter(profile__user=user)
        data = WatchlistSerializer(qs, many=True).data
        return Response(data)
    
get_user_watchlists_api_view = UserWatchlistsAPIView.as_view()

#User Specific Create View
class UserCreateWatchlistAPIView(generics.CreateAPIView,
                                 UserQuerySetMixin):
    queryset = Watchlist.objects.all().order_by('-pk')
    serializer_class = WatchlistSerializer

    def perform_create(self, serializer, *args, **kwargs):
        watchlist = Watchlist.objects.create(
            title=serializer.validated_data.get('title'),
            profile=self.request.user.profile,
        )
        watchlist.save(commit=True)

user_create_watchlist_api_view = UserCreateWatchlistAPIView.as_view()

#User Specific Update View
class UserUpdateWatchlistAPIView(generics.UpdateAPIView,
                                 UserQuerySetMixin):
    queryset = Watchlist.objects.all().order_by('-pk')
    serializer_class = WatchlistSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        watchlist = serializer.save()

user_update_watchlist_api_view = UserUpdateWatchlistAPIView.as_view()

#User Specific Delete View
class UserDeleteWatchlistAPIView(generics.DestroyAPIView,
                                 UserQuerySetMixin):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        # instance 
        super().perform_destroy(instance)

user_delete_watchlist_api_view = UserDeleteWatchlistAPIView.as_view()

#Functionality Request
@api_view(['POST'])
def add_movie_to_watchlist(request, movie_id, watchlist_id):
    if request.method == 'POST' and request.is_ajax():
        movie = Movie.objects.get(id=movie_id)
        watchlist = request.user.watchlist_owner.get(id=watchlist_id)
        if movie in watchlist.movies.all():
            raise Exception('Already in watchlist.')
        else:
            watchlist.movies.add(movie)
            watchlist.save()
        
        return Response({'movie': movie.title, 'added': f'added to the {watchlist.title}'})

# Profile 
class getUserProfileAPIView(generics.RetrieveAPIView,
                            UserQuerySetMixin):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Profile.objects.filter(pk=user.profile.pk)
        return qs
        
    def get(self, request, *args, **kwargs):
        user = request.user
        qs = Profile.objects.filter(pk=user.profile.pk)
        data = ProfileSerializer(qs, many=True).data
        return Response(data)

get_user_profile_api_view = getUserProfileAPIView.as_view()

