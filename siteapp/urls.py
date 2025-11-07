from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("registrar/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    path("usuarios/", views.usuarios, name="usuarios"),
    path("usuarios/novo/", views.usuario_novo, name="usuario_novo"),
    path("usuarios/<int:pk>/editar/", views.usuario_editar, name="usuario_editar"),
    path("usuarios/<int:pk>/excluir/", views.usuario_excluir, name="usuario_excluir"),
]

