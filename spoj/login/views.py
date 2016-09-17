from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib import auth
from .forms import NameForm


def index(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            print("yes")
        else:
            print(form.non_field_errors())
            return render(request, 'login/form.html', {'form': form})
    return render(request, 'login/form.html', {'form': NameForm})
