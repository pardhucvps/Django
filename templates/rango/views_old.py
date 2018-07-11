from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):

    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name_startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page.id']
            # print(page_id)
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                # print('in except')
                pass
    return redirect(url)


def index(request):

    request.session.set_test_cookie()

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    cat_list = get_category_list()
    context_dict = {'categories': category_list, 'pages': page_list, 'cat_list': cat_list}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context=context_dict)
    if request.session.get('last_visit'):
        # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')

        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    return response


def about(request):

    context_dict = {}
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list
    context_dict['bold_message'] = 'Hey partner'
    return render(request, 'rango/index.html', context=context_dict)


def category(request,category_name_slug):

    context_dict = {}
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list


    try:
        category = Category.objects.get(slug = category_name_slug)
        pages = Page.objects.filter(category = category_name_slug).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        pass

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    if not context_dict['query'] :
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):

    cat_list = get_category_list()
    context_dict = {}
    context_dict['cat_list'] = cat_list
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            # print(category, category.slug)
            return index(request)

        else:
            print(form.errors)

    context_dict['form'] = form
    return render(request, 'rango/add_category.html', context_dict)


@login_required
def add_page(request, category_name_slug):

    cat_list = get_category_list()
    context_dict = {}
    context_dict['cat_list'] = cat_list

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    context_dict = {'form': form, }

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
                if category:
                    page = form.save(commit=False)
                    page.category = category
                    page.views = 0
                    page.save()
                    return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict['category'] = category
    context_dict['form'] = form

    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    registered = False
    context_dict = {}
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
            print(registered)
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict['user_form'] = user_form
    context_dict['profile_form']= profile_form
    context_dict['registered'] = registered

    return render(request, 'rango/register.html', context_dict)


def user_login(request):

    context_dict = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username, password)

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse('Your Rango Account is Disabled')
        else:
            print('Invalid Login Details: {0}, {1}'.format(username, password))
            return HttpResponse('Invalid Login Credentials')
    else:
        return render(request, 'rango/login.html', context_dict)


@login_required
def restricted(request):

    return HttpResponse('You can see this because u are logged in')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:

            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


@login_required
def profile(request):

    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render(request, 'rango/profile.html', context_dict)


@login_required
def like_category(request):

    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category.id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)


def suggest_category(request):
    cat_list = []
    starts_with=''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/category_list.html', {'cat_list': cat_list})


@login_required
def auto_add_page(request):
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category.id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=cat_id)
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)


def show_pages(request):
    context_dict = {}
    try:
        pages = Page.objects.all()
        context_dict['page'] = pages
    except Page.DoesNotExist:
        context_dict['page'] = None

    return render(request, 'rango/pages.html', context=context_dict)

