from django.urls import include, path

urlpatterns = [
    path('', include('python_app.urls')),
]
