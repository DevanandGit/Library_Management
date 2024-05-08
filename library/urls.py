from django.urls import path
from .views import (DepartmentListCreateAPIView, DepartmentRetrieveUpdateDestroyAPIView, GenreListCreateAPIView,
GenreRetrieveUpdateDestroyAPIView, BooksListCreateAPIView, BooksRetrieveUpdateDestroyAPIView, RegularUserLoginAPIView,RegularUserRegistrationAPIView,
RegisteredUsers, RegularUserLogoutAPIView, AdminRegistrationAPIView, IssueBookView, IssueBookListAPIView, ReturnBookView, success_page, issue_book,
return_success, return_book, success_page)


urlpatterns = [
    path('admin-reg/', AdminRegistrationAPIView.as_view()),
    path('user-reg/', RegularUserRegistrationAPIView.as_view()),
    path('user-list/', RegisteredUsers.as_view()),
    path('issued-book-list/', IssueBookListAPIView.as_view()),
    path('user-login/', RegularUserLoginAPIView.as_view()),
    path('user-logout/', RegularUserLogoutAPIView.as_view()),
    path('dept-add-list/', DepartmentListCreateAPIView.as_view()),
    path('dept-add-list/<str:id>', DepartmentRetrieveUpdateDestroyAPIView.as_view()),
    path('genre-add-list/', GenreListCreateAPIView.as_view()),
    path('genre-add-list/<str:id>', GenreRetrieveUpdateDestroyAPIView.as_view()),
    path('book-add-list/', BooksListCreateAPIView.as_view()),
    path('book-add-list/<str:id>', BooksRetrieveUpdateDestroyAPIView.as_view()),
    path('issue-book/', IssueBookView.as_view()),
    path('return-book/', ReturnBookView.as_view()),
    path('', issue_book, name='issuebook'),
    path('return/', return_book, name='return_book'),
    path('issue-success/', success_page, name='issueusccess'),
    path('return-success/', return_success, name='return_success'),
]
