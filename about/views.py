from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import About

# Create your views here.
def about_me(request):
    """
    Display an individual :model:`blog.About`.

    **Context**

    ``about``
        An instance of :model:`blog.About`.

    **Template:**

    :template:`blog/about.html`
    """

    # queryset = About.objects.all()
    # about = get_object_or_404(queryset)

    about = About.objects.all().order_by('-updated_on').first()

    return render(
        request,
        "about/about.html",
        {"about": about},
    )
