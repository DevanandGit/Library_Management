from django import forms
from .models import (IssueBook, Department, Genre, Books)

class IssueBookform(forms.ModelForm):
    class Meta:
        model = IssueBook
        fields = ['user','book']


class ReturnBookForm(forms.Form):
    username = forms.CharField(max_length=200)
    book_id = forms.CharField(max_length=200)


