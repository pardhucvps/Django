import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twd_project.settings')

import django
django.setup()

from rango.models import Category, Page


def populate():

    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    #  This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.
    python_pages = [

                    {
                     "title": "Official Python Tutorial",
                     "Category": "Python",
                     "url": "http://docs.python.org/2/tutorial/",
		     "likes": 128, 
 		     "views": 64,
                    },

                    {
                     "title": "How to Think like a Computer Scientist",
                     "Category": "Python",
                     "url": "http://www.greenteapress.com/thinkpython/",
		     "likes": 128, "views": 64,
                    },

                    {
                     "title": "Learn Python in 10 Minutes",
                     "category": "Python",
                     "url": "http://www.korokithakis.net/tutorials/python/",
			"likes": 128, "views": 64,
                    },

                   ]

    django_pages = [
                    {
                     "title": "Official Django Tutorial",
                     "url": "https://docs.djangoproject.com/en/1.9/intro/tutorial01/",
		   "likes": 64, "views": 32,		
                    },

                    {
                     "title": "Django Rocks",
                     "url": "http://www.djangorocks.com/",
			"likes": 64, "views": 32,
		    },

                    {
                     "title": "How to Tango with Django",
                     "url": "http://www.tangowithdjango.com/",
			"likes": 64, "views": 32,
                    }

                   ]

    other_pages = [
                    {
                     "title": "Bottle",
                     "url": "http://bottlepy.org/docs/dev/",
			"likes": 32, "views": 16,
                    },

                    {
                     "title": "Flask",
                     "url": "http://flask.pocoo.org",
			"likes": 32, "views": 16,
                    },

                  ]

    cats = {
            "Python": {"pages": python_pages,},
            "Django": {"pages": django_pages, },
            "Other Frameworks": {"pages": other_pages,},
           }
	 
    for cat, cat_data in cats.items():
        c = add_cat(cat)
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"],p["views"],p["likes"])

    # Print out the categories we have added.

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views=0, likes=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views += views
    p.likes = likes
    p.save()
    return p


def add_cat(name):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = 1
    c.likes = 1
    c.save()
    return c

# Start execution here!


if __name__ == '__main__':
    print("Starting Rango population script...")
    populate()
