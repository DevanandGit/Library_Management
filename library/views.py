from django.shortcuts import render
from .serializer import (BooksSerializer, DepartmentSerializer, GenreSerializer, 
                         IssueBookSerializer, UserSerializer, AdminSerializer, RegularUserLoginSerializer)
from .models import (IssueBook, Department, Genre, Books)
from rest_framework.generics import (CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView,)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import (IsAuthenticated, AllowAny, IsAdminUser)
from rest_framework.filters import SearchFilter
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import ast
from django.utils import timezone
from datetime import timedelta
from django.views.generic import CreateView
from .forms import IssueBookform, ReturnBookForm
from django.shortcuts import render, redirect

class DepartmentListCreateAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'id'


class GenreListCreateAPIView(ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'id'


class BooksListCreateAPIView(ListCreateAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    filter_backends = [SearchFilter]
    search_fields = ['book_name', 'author', 'department__dept_name', 'genre__genre_name','book_slug']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply search filtering
        search_query = self.request.query_params.get('search')
        if search_query:
            # Split the search query into individual words and create a Q object for each word
            search_words = search_query.split()
            search_filter = Q()
            for word in search_words:
                search_filter |= (
                    Q(book_name__icontains=word) |
                    Q(author__icontains=word)|
                    Q(book_slug__icontains=word)|
                    Q(department__dept_name__icontains=word)|
                    Q(genre__genre_name__icontains=word)
                )
            queryset = queryset.filter(search_filter)

        return queryset
    

class BooksRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    lookup_field = 'id'
    

#Regular User login view
class RegularUserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegularUserLoginSerializer
    def post(self, request):
        serializer = RegularUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(request, username=serializer.data['username'], password = serializer.data['password'])
            print(f"iuser is {user}")
            if user is not None and not user.is_anonymous:
                token, _ = Token.objects.get_or_create(user = user)
                response = {
                    "message":"Login Successfull",
                    "token": token.key,
                }
                return Response(response, status = status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=400)
    

class RegularUserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user = user)
            response = {
                'data': serializer.data,
                'token': token.key,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#get all registered user list
class RegisteredUsers(ListAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()


#Regular User Logout view
class RegularUserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        Token.objects.get(user = user).delete()
        return Response({"message": "Logout Successful"}, status=status.HTTP_200_OK)


class AdminRegistrationAPIView(APIView):
    # permission_classes = [IsAdminUser]
    serializer_class = AdminSerializer
    def post(self, request):
        serializer = AdminSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message":"success"},status=status.HTTP_201_CREATED)


class IssueBookView(APIView):
    def post(self, request):
        user_id = request.data.get('user')
        book_ids = request.data.get('book', []) 
        book_ids_lst = ast.literal_eval(book_ids)
        print(type(book_ids_lst))
        issue_date = timezone.now().date()  # Set issue_date to current date
        due_date = issue_date + timedelta(days=7)  # Calculate due_date

        # Create an IssueBook instance and save
        issue_book = IssueBook.objects.create(user_id=user_id, issue_date=issue_date, due_date=due_date)
        issue_book.book.set(book_ids_lst)  # Set the many-to-many relationship

        # Assuming you have a serializer to serialize the response
        serializer = IssueBookSerializer(issue_book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class IssueBookListAPIView(ListAPIView):
    queryset = IssueBook.objects.all()
    serializer_class = IssueBookSerializer

from django.db import transaction

class ReturnBookView(APIView):
    def post(self, request):
        username = request.data.get('username')
        book_id = request.data.get('book_id')
        
        if not username or not book_id:
            return Response({"message": "Username and book_id are required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            book = Books.objects.get(book_id=book_id)
        except Books.DoesNotExist:
            return Response({"message": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Wrap the transaction in a try-except block to handle any database-related errors
        try:
            with transaction.atomic():
                # Create a new IssueBook instance for the user if it doesn't exist
                issued_book, created = IssueBook.objects.get_or_create(user=user)
                
                # Ensure the issued_book instance is saved before modifying its many-to-many relationship
                if created:
                    issued_book.save()
                
                # Remove the book from the many-to-many relationship
                issued_book.book.remove(book)
                
                # Increment the book quantity
                book.quantity += 1
                book.save()
                
                response = {"message": "Successfully returned the book."}
                return Response(response, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def IssueBookViewFormview(request):
    if request.method == 'POST':
        form = IssueBookform(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

def issue_book(request):
    if request.method == 'POST':
        form = IssueBookform(request.POST)
        if form.is_valid():
            issue_book_instance = form.save()
            return redirect('success_page')
    else:

        form = IssueBookform()
    return render(request, 'issue_book_form.html', {'form': form})

def success_page(request):
    return render(request, 'success_page.html')


def return_book(request):
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            # Retrieve username and book_id from the form
            username = form.cleaned_data['username']
            book_id = form.cleaned_data['book_id']
            user = User.objects.get(username=username)
            book = Books.objects.get(book_id=book_id)
            issued_book, created = IssueBook.objects.get_or_create(user=user)
            if created:
                issued_book.save()
                
                # Remove the book from the many-to-many relationship
            issued_book.book.remove(book)
            book.quantity += 1
            book.save()
            return redirect('return_success')
    else:
        form = ReturnBookForm()
    return render(request, 'return_book_form.html', {'form': form})

def return_success(request):
    # Render a success page after the book is successfully returned
    return render(request, 'return_success.html')