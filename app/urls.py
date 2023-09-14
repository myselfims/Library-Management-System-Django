from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list),
    path('dashboard/', views.dashboard),
    path("issuebook/<int:id>/",views.issueBook),
    path("returnbook/<int:id>/",views.returnBook),
    path("members/",views.members),
    path("addmember/",views.addMember),
    path("deletemember/<int:id>",views.deleteMember),
    path("addbooks/",views.addBooks),
    path("deletebook/<int:id>",views.deleteBook),
    path("search/",views.search),
    
]
