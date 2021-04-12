from django.shortcuts import render,redirect
from django.views.generic.base import View
from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponse


from django.db.models import Q
from .models import Movie, Category, Actor, Genre, Rating, RatingStar
from .forms import ReviewForm, RatingForm

# Create your views here.



class GenreYear:

	def get_genres(self):
		return Genre.objects.all()


	def get_years(self):
		return Movie.objects.filter(draft=False).values('year')


class MovieListView(GenreYear, ListView):

	model = Movie
	queryset = Movie.objects.filter(draft=False)
	paginate_by=1

	# def get_context_data(self, *args, **kwargs):
	# 	context = super().get_context_data(*args,**kwargs)
	# 	context['categories']=Category.objects.all()
	# 	return context


class MovieDetailView(GenreYear, DetailView):
	model=Movie
	slug_field="url"

	def get_context_data(self,*args, **kwargs):
		context=super().get_context_data(**kwargs)
		# check if user already has star on movie 
		ip = AddStarRating.get_client_ip(self,self.request)
		movie_id = Movie.objects.get(url=context['movie'].url).id
		stars = None
		if Rating.objects.filter(ip=ip, movie_id=movie_id).exists():
			stars = Rating.objects.get(ip=ip, movie_id=movie_id).star
		if stars:
			context['stars'] = str(stars)
		
		# calculate number of users. Then looking average star star queryset
		# paste average star in context and send on to front-end 
		users_number=Rating.objects.filter(movie_id=movie_id).count()
		if users_number > 0:
			star_queryset=Rating.objects.get(movie_id=movie_id).star.rating_set.all()
			average_star = sum([star_queryset.values()[i]['star_id'] for i in range(users_number)]) / users_number
			context['average_star'] = str(average_star)
		context['star_form'] = RatingForm()
		context['form'] = ReviewForm()
		return context


class AddReview(View):
	
	def post(self, request, pk):
		form=ReviewForm(request.POST)
		movie=Movie.objects.get(id=pk)
		if form.is_valid():
			form=form.save(commit=False)
			if request.POST.get("parent", None):
				form.parent_id=int(request.POST.get("parent"))
			form.movie=movie
			form.save()
		return redirect(movie.get_absolute_url())



class ActorDetail(GenreYear, DetailView):
	model=Actor
	slug_field="name"
	template_name="movie/actor.html"



class FilterMovieView(GenreYear, ListView):

	paginate_by=2

	def get_queryset(self):
		queryset = Movie.objects.filter(
			Q(year__in=self.request.GET.getlist("year")) |
			Q(genres__in=self.request.GET.getlist("genre"))
		).distinct()
		return queryset

	def get_context_data(self, *args,**kwargs):
	    context = super().get_context_data(*args,**kwargs)
	    context["genre"]=''.join([f'genre={x}&' for x in self.request.GET.getlist("genre")])
	    context["year"]=''.join([f'year={x}&' for x in self.request.GET.getlist("year")])
	    return context


class AddStarRating(View):

	def get_client_ip(self, request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip=x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip
		

	def post(self, request):
		form = RatingForm(request.POST)
		if form.is_valid():
			Rating.objects.update_or_create(
				ip=self.get_client_ip(request),
				movie_id=int(request.POST.get('movie')),
				defaults={'star_id': int(request.POST.get("star"))}
			)
			return HttpResponse(status=201)
		else:
			return HttpResponse(status=400)						


class Search(GenreYear, ListView):

	paginate_by=1

	def get_queryset(self):
		q = self.request.GET.get('q')
		a = ''.join(q[0].upper() + q[1:])
		return Movie.objects.filter(title__icontains=a)


	def get_context_data(self, *args,**kwargs):
	    context = super().get_context_data(*args,**kwargs)
	    context["q"]=f'q={self.request.GET.get("q")}&'
	    return context


