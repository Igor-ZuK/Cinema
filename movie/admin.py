from django import forms
from django.contrib import admin
from django.utils.html import mark_safe

# //---CKEditor in Flatpages---//
from django.db import models
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget
# //--------------------------//

# //---Regular CKEditor in django admin---///
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from modeltranslation.admin import TranslationAdmin


from .models import Category,Actor, Genre, Movie, MovieShots, RatingStar, Rating, Reviews


# //---CKEditor in Flatpages---//
# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

# //--------------------------//


class MovieAdminForm(forms.ModelForm):
	description_ru=forms.CharField(label="Описание", widget=CKEditorUploadingWidget())
	description_en=forms.CharField(label="Description", widget=CKEditorUploadingWidget())

	class Meta:
		model = Movie
		fields= '__all__'


class ActorAdminForm(forms.ModelForm):
	description_ru=forms.CharField(label="Описание", widget=CKEditorUploadingWidget())
	description_en=forms.CharField(label="Description", widget=CKEditorUploadingWidget())

	class Meta:
		model = Actor
		fields= '__all__'


# Register your models here.
@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
	list_display=('name', 'description', 'url')
	list_display_links=('name', )
	search_fields=('name', 'description', 'url')



class ReviewInLines(admin.StackedInline): #можно и Tabular
	model=Reviews
	extra=1
	readonly_fields=('name','email')



@admin.register(Actor)
class ActorAdmin(TranslationAdmin):
	list_display=('name', 'age', 'get_image')
	readonly_fields=('get_image',)
	list_display_links=('name',)
	search_fields=('name', 'age',)
	save_on_top=True
	form=ActorAdminForm

	def get_image(self, obj):
		return mark_safe(f'<img src={ obj.image.url } width="50" height="60" >')

	get_image.short_description="Изображение"


class MovieShotsInLine(admin.TabularInline):
	model=MovieShots
	extra=1
	readonly_fields=('get_image',)

	def get_image(self, obj):
		return mark_safe(f'<img src={ obj.image.url } width="100" height="110" >')

	get_image.short_description="Изображение"


@admin.register(Movie)
class MovieAdmin(TranslationAdmin):
	list_display=('title','category','tagline', 'url', 'draft')
	list_display_links=('title','tagline', 'url' )
	list_filter=('category','year')
	search_fields=('title','category__name', 'tagline','url')
	inlines=[ MovieShotsInLine,ReviewInLines,]
	save_on_top=True
	save_as=True
	list_editable=('draft',)
	actions = ['publish', 'unpublish']
	form=MovieAdminForm
	readonly_fields=('get_image',)
	fieldsets=(
		(None,{
			'fields':('title', 'category', 'tagline')
		}),
		("Actors",{
			'classes':('collapse',),
			'fields':(('actors', 'directors', 'genres'),)
		}),
		(None,{
			'fields':('description', ('poster', 'get_image'))
		}),
		(None,{
			'fields':(('budget', 'fees_in_usa', 'fees_in_world'),)
		}),
		(None,{
			'fields':(('year', 'world_primiere'),)
		}),
		(None,{
			'fields':('country',)
		}),
		(None,{
			'fields':(('url','draft'),)
		}),
	)

	def get_image(self, obj):
		return mark_safe(f'<img src={ obj.poster.url } width="100" height="110" >')


	def publish(self, request, queryset):
		row_update = queryset.update(draft=False)
		if row_update==1:
			message_bit="1 запись обновлена"
		else:
			message_bit=f'{row_update} записей обновлены'
		self.message_user(request, f'{message_bit}')
		

	def unpublish(self, request, queryset):
		row_update = queryset.update(draft=True)
		if row_update==1:
			message_bit="1 запись обновлена"
		else:
			message_bit=f'{row_update} записей обновлены'
		self.message_user(request, f'{message_bit}')


	publish.short_description='Опубликовать'
	publish.allowed_permissions=('change',)


	unpublish.short_description='Снять с публикации'
	unpublish.allowed_permissions=('change',)


	get_image.short_description="Постер"



@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
	list_display=('name', 'email','parent', 'movie', 'id')
	readonly_fields=('name', 'email')
	list_display_links=('name', 'movie')
	search_fields=('name', 'text')



@admin.register(MovieShots)
class MovieShotsAdmin(TranslationAdmin):
	list_display=('title', 'movie','get_image')
	readonly_fields=('get_image',)
	list_filter=('movie',)
	list_display_links=('title',)
	search_fields=('title', 'movie')
	save_on_top=True
	save_as=True


	def get_image(self, obj):
		return mark_safe(f'<img src={ obj.image.url } width="50" height="60" >')

	get_image.short_description="Изображение"


@admin.register(Genre)
class GenreAdmin(TranslationAdmin):
	list_display=('name', 'url')
	list_display_links=('name',)
	search_fields=('name',)
	save_on_top=True



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("star", "movie", "ip")



# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(RatingStar)


admin.site.site_title="Django Movies"
admin.site.site_header="Django Movies"


