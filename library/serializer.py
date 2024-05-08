from rest_framework import serializers
from .models import (IssueBook, Department, Genre, Books)
from django.contrib.auth.models import User



class BooksSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    genre = serializers.StringRelatedField()
    class Meta:
        model = Books
        fields = ['id','book_name', 'book_id','book_image','department', 'genre', 'author', 'published_date', 'quantity', 'book_slug']


class DepartmentSerializer(serializers.ModelSerializer):
    books = BooksSerializer(many = True, read_only = True)
    class Meta:
        model = Department
        fields = ['id','dept_name','dept_slug' ,'books']


class GenreSerializer(serializers.ModelSerializer):
    books = BooksSerializer(many = True, read_only = True)
    class Meta:
        model = Genre
        fields = ['id','genre_name', 'books']


class IssueBookSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    book = serializers.StringRelatedField(many=True)
    class Meta:
        model = IssueBook
        fields = ['id','user', 'book', 'issue_date', 'due_date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        book_representation = representation['book']

        if isinstance(book_representation, list):
            # If book_representation is a list, return all items
            representation['book'] = book_representation
        elif book_representation is not None:
            # If book_representation is not a list and not None, convert it to a list
            representation['book'] = [book_representation]

        return representation



class UserSerializer(serializers.ModelSerializer):
    books_issued = IssueBookSerializer(many = True, read_only = True)
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.RegexField(
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'invalid': 'Password must contain at least 8 characters, including uppercase, lowercase, and numeric characters.'
        }
    )
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'username', 'password', 'confirm_password', 'books_issued']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Password mismatch')
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user
    

class AdminSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.RegexField(
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'invalid': 'Password must contain at least 8 characters, including uppercase, lowercase, and numeric characters.'
        }
    )
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'username', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Password mismatch')
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_superuser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user
    

class RegularUserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length = 300)
    password = serializers.CharField(max_length=128)