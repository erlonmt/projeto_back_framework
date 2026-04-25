from django.urls import path

from . import views

app_name = "teleagendamento"

urlpatterns = [
    path("", views.ConsultaListView.as_view(), name="consulta_list"),
    path("consultas/nova/", views.ConsultaCreateView.as_view(), name="consulta_create"),
    path(
        "consultas/<int:pk>/editar/",
        views.ConsultaUpdateView.as_view(),
        name="consulta_update",
    ),
    path(
        "consultas/<int:pk>/remover/",
        views.ConsultaDeleteView.as_view(),
        name="consulta_delete",
    ),
]
