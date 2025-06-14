# codestar_blog

## Step 1: Planning for a new app

### 1) User stories:
 - Use the user story to draft user stories for the app
 - add clear acceptance criteria

### 2) ERD sketches
- Think about fields required, field types, and relationship between fields
- ERD app can be used or handwritten sketch


## Step 2: Creating a new app 

### 1) settings.py - creating app

- terminal: `python3 manage.py startapp my_app`

- settings.py: add 'my_app' to INSTALLED_APPS 

###  2) 'app'/models.py - add MyApp class and fields:

`class About(models.Model):
    title = models.CharField(max_length=200)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()

    def __str__(self):
        return self.title`

### 3) Migrations

- terminal: `python3 manage.py makemigrations`
- terminal: `python3 manage.py migrate`

### 4) 'app'/admin.py

- add summernote and import relevant packages like below

`from django.contrib import admin
from .models import About
from django_summernote.admin import SummernoteModelAdmin


@admin.register(About)
class AboutAdmin(SummernoteModelAdmin):

    summernote_fields = ('content',)`


### 4) 'app'/views.py

- define function-based views
- get model object, render to template

`from django.shortcuts import render
from .models import About


def about_me(request):
    """
    Renders the About page
    """
    about = About.objects.all().order_by('-updated_on').first()

    return render(
        request,
        "about/about.html",
        {"about": about},
    )`


### 5) templates/base.html

add url alias: `{% url 'about' as about_url %}`

- nav item: 
    <li class="nav-item">
        <a class="nav-link
        {% if request.path == about_url %}active{%endif%}" aria-current="page" href="{% url 'about' %}" >About</a>
    </li>

- Add variable using the passed object e.g. `{{ about.title }}`

- Text containing styling: `{{ about.content | safe }}`


### 6) 'app'/urls.py add:

    `from . import views
    from django.urls import path

    urlpatterns = [
        path('', views.about_me, name='about'),
    ]`

### 7) my_project/urls.py add: 

    `from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path("about/", include("about.urls"), name="about-urls"),
        path('admin/', admin.site.urls),
        path('summernote/', include('django_summernote.urls')),
        path("", include("blog.urls"), name="blog-urls"),
    ]`


## Step 3: Evaluate newly created features against user stories

- Check if each user story has been completed.
- This must be assessed from user's perspective (e.g. if login for specific user role/privileges )


## Step 4: Deploy the project

- Adjust the DEBUG in settings.py

- Run collectstatic (not necessary on Heroku)
    `python manage.py collectstatic`

# Creating a form

## Step 1: User stories
- Add acceptance criteria
- Consider if multiple user stories are necessary (one feature per user story)

## Step 2: in about/models.py
- Create a model for the form
- specify fields for the DB table
- add __str__ to name each items, UX for admin

`class CollaborateRequest(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Collaboration request from {self.name}"`

## Step 3: Run migrations
`python3 manage.py makemigrations`
`python3 manage.py migrate`

## Step 4: Create about/forms.py
add code:
- CollaborateRequest created in models
- fields ('name','email','messages'): collected from the form
- fields specified by admin e.g. 'read' or auto-generated should be excluded 

`from .models import CollaborateRequest
from django import forms


class CollaborateForm(forms.ModelForm):
    class Meta:
        model = CollaborateRequest
        fields = ('name',
                  'email',
                  'message',)`

## Step 5: Add form code to about.html
- Add crispy_forms_tags at the top above '{% block content %}'
    `{% load crispy_forms_tags %}`
- Include `{% csrf_token %}` inside the form
- `collaborate_form` is the specified name in the return 'context' in views.py
- specify 'crispy' as a styling method `{{ collaborate_form | crispy }}`

- Add Html code for the form
    `    <div class="row justify-content-center">
        <div class="col-12 col-md-6 my-5">
            <h2>Let's collaborate!</h2>
            <p>I believe in the power of shared knowledge and collective effort.
                Whether you have a project in mind, wish to co-author
                an article, or simply want to brainstorm some ideas,
                I'm excited to hear from you. Fill out the form
                and we can get the ball rolling!</p>

            <!-- add your form here. Your submit button should 
                                have the classes of btn, btn-secondary -->
            <form  method="post" >
                {{ collaborate_form | crispy }}
                {% csrf_token %}
                <button id="submitButton" type="submit" class="btn btn-secondary">Submit</button>
            </form>
        </div>
    </div>`

## Step 5: Handle from request and submission to DB
- import messages `from django.contrib import messages`
- import the form `from .forms import CollaborateForm`
- Add if statement for 'POST' requests
- No need for `comment = comment_form.save(commit=False)` as no new fields need to be added
- Save data if data is valid `collaborate_form.save()`
- display feedback message to user `messages.add_message(request, messages.SUCCESS,'My message to you')` 

from django.shortcuts import render
from django.contrib import messages
from .models import About
from .forms import CollaborateForm

    `def about_me(request):

        if request.method == "POST":
            collaborate_form = CollaborateForm(data=request.POST)
            if collaborate_form.is_valid():
                collaborate_form.save()
                messages.add_message(request, messages.SUCCESS, "Collaboration request received! I endeavour to respond within 2 working days.")

        about = About.objects.all().order_by('-updated_on').first()
        collaborate_form = CollaborateForm()

        return render(
            request,
            "about/about.html",
            {
                "about": about,
                "collaborate_form": collaborate_form
            },
        )`

- Source code so far: https://github.com/Code-Institute-Solutions/django-blog-sourcecode/tree/main/12-views-part-3/12.8-challenge-handle-the-form-post-request

# Creating CRUD capabilities for users

## Step 1: Importing necessary packages in blog/views.py
- import reverse `from django.shortcuts import render, get_object_or_404, reverse`
- import HttpResponseRedirect `from django.http import HttpResponseRedirect`
- import Comment model `from .models import Post, Comment`

## Step 2: Add new views in blog/views.py
- add view named `comment_edit` at the bottom
- This view returns you to the post webpage after you've edited the comment. 
- This return is done with a HttpResponseRedirect and reverse to refresh the post_detail view

    `def comment_edit(request, slug, comment_id):
        """
        view to edit comments
        """
        if request.method == "POST":

            queryset = Post.objects.filter(status=1)
            post = get_object_or_404(queryset, slug=slug)
            comment = get_object_or_404(Comment, pk=comment_id)
            comment_form = CommentForm(data=request.POST, instance=comment)

            if comment_form.is_valid() and comment.author == request.user:
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.approved = False
                comment.save()
                messages.add_message(request, messages.SUCCESS, 'Comment Updated!')
            else:
                messages.add_message(request, messages.ERROR, 'Error updating comment!')

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))`


## Step 3: In the blog/urls.py file, create a URL to point to this new view.
`    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('<slug:slug>/edit_comment/<int:comment_id>',
         views.comment_edit, name='comment_edit'),
]`

## Step 4: Add edit button in post_detail.html
- visible to users to are `logged in` and `are author of the comment`

`{% if user.is_authenticated and comment.author == user %}
  <button class="btn btn-edit"
    comment_id="{{ comment.id }}">Edit</button>
  {% endif %}`

## Step 5: Use JS to construct edit comment URL
- create `static/js/comments.js`
- Add code: 

    `const editButtons = document.getElementsByClassName("btn-edit");
    const commentText = document.getElementById("id_body");
    const commentForm = document.getElementById("commentForm");
    const submitButton = document.getElementById("submitButton");

    /**
    * Initializes edit functionality for the provided edit buttons.
    * 
    * For each button in the `editButtons` collection:
    * - Retrieves the associated comment's ID upon click.
    * - Fetches the content of the corresponding comment.
    * - Populates the `commentText` input/textarea with the comment's content for editing.
    * - Updates the submit button's text to "Update".
    * - Sets the form's action attribute to the `edit_comment/{commentId}` endpoint.
    */
    for (let button of editButtons) {
    button.addEventListener("click", (e) => {
        let commentId = e.target.getAttribute("comment_id");
        let commentContent = document.getElementById(`comment${commentId}`).innerText;
        commentText.value = commentContent;
        submitButton.innerText = "Update";
        commentForm.setAttribute("action", `edit_comment/${commentId}`);
    });
    }`


## Step 6: Add block extras to import js script
- added below `{% endblock content %}`

`{% block extras %}
<script src="{% static 'js/comments.js' %}"></script>
{% endblock %}`

- Add the same block tag only to `base.html`
    `{% block extras %}
     {% endblock %}`

- Make sure DEBUG is set to TRUE, run and test it


## Step 7: Deleting a comment
- Add `comment_delete` in blog/views.py below `comment_edit`

    `def comment_delete(request, slug, comment_id):
        """
        view to delete comment
        """
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comment = get_object_or_404(Comment, pk=comment_id)

        if comment.author == request.user:
            comment.delete()
            messages.add_message(request, messages.SUCCESS, 'Comment deleted!')
        else:
            messages.add_message(request, messages.ERROR, 'You can only delete your own comments!')

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))`


## Step 8: Add urlpattern for comment_delete in blog/urls.py
- `path('<slug:slug>/delete_comment/<int:comment_id>',
         views.comment_delete, name='comment_delete'),`


## Step 9: Add 'Delete' button in post_detail.html
- Added above edit button
- added inside the `{% if %}` tag
<button class="btn btn-delete"
    comment_id="{{ comment.id }}">Delete</button>

## Step 10: Add confirmation step for delete
- add modal that appears after clicking 'Delete' button
- Message sates: "Are you sure you want to delete your comment? This action cannot be undone"
- html code added above `{% endblock content %}`

    `<!-- Delete confirmation modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1"
    aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title"
            id="deleteModalLabel">Delete comment?</h5>
            <button type="button" class="btn-close"
            data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
            Are you sure you want to delete your comment?
            This action cannot be undone.
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary"
            data-bs-dismiss="modal">Close</button>
            <a id="deleteConfirm" href="#" class="btn
            btn-danger">Delete</a>
        </div>
        </div>
    </div>
    </div>`


## Step 11: Wire confirmation modal in JS
`const deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));
const deleteButtons = document.getElementsByClassName("btn-delete");
const deleteConfirm = document.getElementById("deleteConfirm");`

- At the bottom of the comments.js script add:

    `/**
    * Initializes deletion functionality for the provided delete buttons.
    * 
    * For each button in the `deleteButtons` collection:
    * - Retrieves the associated comment's ID upon click.
    * - Updates the `deleteConfirm` link's href to point to the 
    * deletion endpoint for the specific comment.
    * - Displays a confirmation modal (`deleteModal`) to prompt 
    * the user for confirmation before deletion.
    */
    for (let button of deleteButtons) {
    button.addEventListener("click", (e) => {
        let commentId = e.target.getAttribute("comment_id");
        deleteConfirm.href = `delete_comment/${commentId}`;
        deleteModal.show();
    });
    }`

- source code so far: https://github.com/Code-Institute-Solutions/django-blog-sourcecode/tree/main/12-views-part-3/12.9-editing-and-deleting-records
- Test, Git add, commit and push
- Change DEBUG to False

# Setting up Cloudinary: Media storage
- Change DEBUG to True

## Step 1: Install required packages
`pip3 install cloudinary~=1.36.0 dj3-cloudinary-storage~=0.0.6 urllib3~=1.26.15`
`pip3 freeze --local > requirements.txt`

## Step 2: Sign up for a cloudinary account
- email or google account
- From `Cloudinary Dashboard` click on the `Go to API Keys`
- copy `CLOUDINARY_URL=cloudinary://<your_api_key>:<your_api_secret>@dltmrnhmx`

- Add os.environ to eny.py
`os.environ.setdefault("CLOUDINARY_URL", "cloudinary://<your_api_key>:<your_api_secret>@dltmrnhmx")`

## Step 3: Add cloudinary_storage and cloudinary to INSTALLED_APPS in my_project/setting.py
- `cloudinary_storage` must be added below `django.contrib.staticfiles`
- `cloudinary` added above the first custom app, below summernote if it exists

## Step 4: Update blog app to use Cloudinary
- Import CloudinaryField in blog/models.py
`from cloudinary.models import CloudinaryField`

## Step 5: Add field in the Post model to store image for each post
- added below author field `featured_image = CloudinaryField('image', default='placeholder')`

## Step 6: Run makemigrations and migrates
`python manage.py makemigrations`
`python manage.py migrate`

## Step 7: Add DTL loop within from image-container in the blog/templates/blog/index.html
- Add `{% load static %}` at the top, below `{% extends ...%}`
    `{% if "placeholder" in post.featured_image.url %}
    <img class="card-img-top" src="{% static 'images/default.jpg' %}"
        alt="placeholder image">
    {% else %}
    <img class="card-img-top" src=" {{ post.featured_image.url }}" alt="{{ post.title }}">
    {% endif %}`

- Code so far: https://github.com/Code-Institute-Solutions/django-blog-sourcecode/tree/main/13-where-to-put-things/13.2-storing-images-on-cloudinary
- Change DEBUG to False and save all files
- Git add, commiit and push
    `git add --all`
    `git commit -m "enable serving of image files"`
    `git push origin main`

## Step 8: Add CLOUDINARY_URL to ConfigVars in Heroku
- Create a key value pair and copy contents in the env.py
- `Deploy Branch` and check the updates

# Tidying up project:

## Step 1: HTML validation
- cannot use direct html input from templates - DTL not recognized
- validate by URI using the deployed application from Heroku
- on W3C website, select `Validate by URI` then pass the link to the relevant page:
`https://codestar-app-blog-9cdb6fc38d19.herokuapp.com/about/`

- For content show by conditions i.e. logged in users only:
- Get the 'page source' copy content and 'Validate by Direct Input' 

## Step 2: Improve UX display for messages
- in my_project/settings.py import `from django.contrib.messages import constants as messages`
- Add MESSAGES_TAGS as a dict
- Added below `USE_TZ = True`
    `MESSAGES_TAGS = {
    messages.SUCCESS: 'alert-success',
    messages.ERROR: 'alert-danger',
    }`

## Step 3: Check the loops for error/ no hardcoded
- e.g. `aria-current="page{% endif %}"` was exluded from the loop, setting every page as current page

## Step 4: for elements that may contain other hmtl elements, ensure its permissible:
- E.g. content passed in the `<p></p>` tags also contain other block level elements
- replace `<p>` tags with `<article>`

## Step 5: Backend code must be validated too
- check all python files e.g `views.py`
- Imports must be grouped into standard library imports, third-party imports and local import - in this order
- Docstring must be added to all custom functions and classed
- Not the django framework boilerplate
- required for: `models` and `views`
- Add docstring for `admin.py`,`apps.py` and `forms.py` classes and functions
- PEP8 docstring convention - https://peps.python.org/pep-0257/
- source code in the end: https://github.com/Code-Institute-Solutions/django-blog-sourcecode/tree/main/13-where-to-put-things/13.4-tidying-up

## Step 6: Check all user stories have been completed
- Click close issue for completed ones


# Testing: Django testing 

## Automated Testing: Forms
- Django creates its own database for testing. Don't use live Postgres database - use the built-in SQLite3 database

### Setup SQLite3 database
1) Import: `import sys` below `os` import in my_project/settings.py

2) Below DATABASES in my_project/settings.py
- Add:
    if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

### Create test: Forms
1) Duplicate blog/test.py
- name the copy `test_forms.py`

2) Add code to blog/test_forms.py:
`from .forms import CommentForm


class TestCommentForm(TestCase):

    def test_form_is_valid(self):
        comment_form = CommentForm({'body': 'This is a great post'})
        self.assertTrue(comment_form.is_valid())`

3) Run the test
`python manage.py test`

- If test passes, . and OK is returned else fail is shown
- Custom message can be added as arg
`self.assertTrue(comment_form.is_valid(), msg='Form is not valid')`

- There are different asset methods in django's testing library  

4) Testing collaboration form - mutliple fields:

class TestCollaborateForm(TestCase):

    def test_form_is_valid(self):
        """ Test for all fields"""
        form = CollaborateForm({
            'name': '',
            'email': 'test@test.com',
            'message': 'Hello!'
        })
        self.assertTrue(form.is_valid(), msg="Form is not valid")

5) Specify which test to run
`python3 manage.py test` for all tests
`python3 manage.py test about.test_forms. TestCollaborateForm` only for TestCollaborateForm in about/test_forms.py

Refer to cheat sheet: https://codeinstitute.s3.eu-west-1.amazonaws.com/hello-blog/django_cheatsheet.zip

### Create test: Views setup mock data

1) Code in blog/views.py:
- `def setUp(self):` This provide initial setting which can be used later
- create a superuser and submit a post -m results assigned to `self`
- `User.objects.create_superuser()` is used to create a superuser
- Provide a value for args if the URL you are building in reverse expects them. 
- check what URLs expect in the urls.py file

class TestBlogViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="myUsername",
            password="myPassword",
            email="test@test.com"
        )
        self.post = Post(title="Blog title", author=self.user,
                         slug="blog-title", excerpt="Blog excerpt",
                         content="Blog content", status=1)
        self.post.save()

    def test_render_post_detail_page_with_comment_form(self):
        response = self.client.get(reverse(
            'post_detail', args=['blog-title']))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Blog title", response.content)
        self.assertIn(b"Blog content", response.content)
        self.assertIsInstance(
            response.context['comment_form'], CommentForm)


