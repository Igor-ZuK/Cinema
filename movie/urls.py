from django.urls import path
from . import views


urlpatterns = [
   path('', views.MovieListView.as_view() ,name='index'),
   path("filter/", views.FilterMovieView.as_view(), name='movie_filter'),
   path('search/', views.Search.as_view(), name='search'),
   path('add-rating/', views.AddStarRating.as_view(), name='add_rating'),
   path('<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
   path('review/<int:pk>', views.AddReview.as_view(), name='add_review'),
   path('actor/<str:slug>', views.ActorDetail.as_view(), name='actor_detail'),
]
