from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import About
from .forms import CollaborateForm

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

    collaborate_form = CollaborateForm()
    # collaborate_form = CollaborateForm(data=request.POST)
    # if collaborate_form.is_valid():
    #     collaboration = collaborate_form.save(commit=False)
    #     # comment.author = request.user
    #     # comment.post = post
    #     collaboration.save()
    #     messages.add_message(
    #         request, messages.SUCCESS,
    #         'Collaboration request submitted successfully'
    #     )

    # queryset = About.objects.all()
    # about = get_object_or_404(queryset)

    about = About.objects.all().order_by('-updated_on').first()

    return render(
        request,
        "about/about.html",
        {"about": about,
         "collaborate_form": collaborate_form,
         },
    )
