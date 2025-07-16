from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # URLs das aplicações
    path('', include('fazendascdst.urls')),  
    path('gado/', include('gado.urls')),
    path('estoque/', include('estoque.urls')),
    path('relatorios/', include('relatorios.urls')),
]
