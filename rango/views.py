from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, User, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.shortcuts import redirect


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def index(request):
	#request.session.set_test_cookie()
	category_list = Category.objects.order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]

	context_dict = {'categories':category_list, 'pages':pages_list}
	#context_dict['visits'] = request.session['visits']
	#response= render(request, 'rango/index.html', context=context_dict)

	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	return render(request, 'rango/index.html', context=context_dict)


def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
	print(request.method)
	print(request.user)
	context_dict = {'boldmessage':"Hey There"}
	return render(request, 'rango/about.html', context=context_dict)


def visitor_cookie_handler(request):

	visits_cookie = int(request.COOKIES.get('visits', '1'))
	last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
# If it's been more than a day since the last visit...
	visits=visits_cookie
	if (datetime.now() - last_visit_time).days > 0:
		visits = visits + 1
#update the last visit cookie now that we have updated the count
		request.session['last_visit'] = str(datetime.now())
	else:
# set the last visit cookie
		request.session['last_visit'] = last_visit_cookie
# Update/set the visits cookie
	request.session['visits'] = visits


def show_category(request,category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['page'] = None
    return render(request,'rango/category.html', context_dict)


def add_category(request):
    form = CategoryForm()
    if request.method=='POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors())
    return render(request,'rango/add_category.html',{'form':form})


def add_page(request,category_name_slug):

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request,category_name_slug)
            else:
                print(form.errors())
    context_dict = {'form':form,'category':category}
    return render(request,'rango/add_page.html', context_dict)


def register(request):
    registered = False
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
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered})


def user_login(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password = password )
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango Account is disabled. ")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied. ")
    else:
        return render(request, 'rango/login.html', {})


def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in. ")
    else:
        return HttpResponse("You are not logged in. ")


@login_required
def restricted(request):
    return HttpResponse("Since you are logged in, you can see this text!")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


from rango.bing_search import run_query
def search(request):
	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
# Run our Bing function to get the results list!
			result_list = run_query(query)
	return render(request, 'rango/search.html', {'result_list': result_list})




def track_url(request):
	page_id=None
	url='/rango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url
			except:
				pass
	return redirect(url)


@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
	likes = 0
	if cat_id:
		cat = Category.objects.get(id=int(cat_id))
		if cat:
			likes = cat.likes + 1
			cat.likes = likes
			cat.save()
	return HttpResponse(likes)


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


def get_category_list(max_results=0,starts_with=''):
	cat_list=[]
	if starts_with:
		cat_list=Category.objects.filter(name__istartswith=starts_with)
	if(max_results>0):
		if len(cat_list)>max_results:
			cat_list=cat_list[:max_results]
	return cat_list


def suggest_category(request):
	cat_list=[]
	starts_with=''
	if request.method=='GET':
		starts_with=request.GET['suggestion']
	cat_list=get_category_list(8,starts_with)
	return render(request,'rango/category_list.html',{'cat_list':cat_list})