from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.text import slugify
from django.utils import timezone

# product_slug = models.SlugField(blank=True, null=True)
#     other_field = models.CharField(max_length=150, null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     if not self.product_slug:
    #         self.product_slug = slugify(self.product_name)
    #     return super().save(*args, **kwargs)

class Department(models.Model):
    dept_name = models.CharField(max_length = 300)
    dept_slug = models.SlugField(blank=True, null=True)

    
    def save(self, *args, **kwargs):
        if not self.dept_slug:
            self.dept_slug = slugify(self.dept_name)
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.dept_name}"
    

class Genre(models.Model):
    genre_name = models.CharField(max_length = 300)
    genre_slug = models.SlugField(blank=True, null=True)

    
    def save(self, *args, **kwargs):
        if not self.genre_slug:
            self.genre_slug = slugify(self.genre_name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.genre_name}"
    

class Books(models.Model):
    book_name = models.TextField()
    book_image = models.ImageField(upload_to='books/images/', blank=True, null=True)
    book_id = models.CharField(max_length=10, default=0, blank=False, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='books', null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    author = models.CharField(max_length = 300)
    published_date = models.DateField()
    quantity = models.IntegerField(default=0)
    book_slug = models.SlugField(blank=True, null=True)

    
    def save(self, *args, **kwargs):
        if not self.book_slug:
            self.book_slug = slugify(self.book_name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.book_name}"



class IssueBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_issued')
    book = models.ManyToManyField(Books)
    issue_date = models.DateField(null=True, blank=True)  # Allow issue_date to be nullable
    due_date = models.DateField(null=True, blank=True)  # Allow due_date to be nullable

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new object
            self.issue_date = timezone.now().date()  # Set issue_date to current date
            self.due_date = self.issue_date + timedelta(days=7)  # Calculate due_date
        super().save(*args, **kwargs)
