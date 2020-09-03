from django.shortcuts import render


def index(request):
    if request.user.is_authenticated:
        return render(request, "projects.html", {})
    else:
        return render(request, "index.html", {})
