from django.contrib import admin

# Register your models here.
from .models import (IssueBook, Department, Genre, Books)


admin.site.register(IssueBook)
admin.site.register(Department)
admin.site.register(Genre)
admin.site.register(Books)
