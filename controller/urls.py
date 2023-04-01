from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_home, name='api_home'),
    #Movie Router
    path('get_movie_list/', views.movie_list_api_view, name='rest_get_movie_list'),
    path('get_movie_details/<str:listz_id>/', views.movie_detail_api_view, name='rest_get_movie_details'),
    path('create_movie/', views.movie_create_api_view, name='rest_create_movie'),
    path('get_movie_details/<str:pk>/update', views.movie_update_api_view, name='rest_movie_update'),
    path('get_movie_details/<str:pk>/delete', views.movie_update_api_view, name='rest_movie_delete'),
    #Watchlist Router
    path('get_watchlists/', views.watchlists_api_view, name='rest_get_watchlists'),
    path('get_watchlists/<str:user>/', views.get_user_watchlists_api_view, name='rest_get_user_watchlist'),
    path('create_watchlist/', views.user_create_watchlist_api_view, name='rest_create_user_watchlist'),
    path('update_watchlist/<str:pk>/', views.user_update_watchlist_api_view, name='rest_update_user_watchlist'),
    path('delete_watchlist/<str:pk>/', views.user_delete_watchlist_api_view, name='rest_delete_user_watchlist'),
    path('add_movie_to_watchlist/<str:movie_id>/<str:watchlist_id/', views.add_movie_to_watchlist, name='rest_add_movie_to_watchlist'),
    #User Router
    path('profile/', views.get_user_profile_api_view, name='rest_profile'),
]