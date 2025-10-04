from django.urls import path

from . import views

urlpatterns = [
    path("go/note-detail/", views.go_note_detail, name="go_note_detail"),
    path("purchased/note/", views.purchased_note, name="purchased_note"),
]
