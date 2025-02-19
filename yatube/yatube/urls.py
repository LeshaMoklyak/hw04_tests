from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),

]
