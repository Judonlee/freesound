from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from sounds.models import Sound
from bookmarks.models import *
from bookmarks.forms import BookmarkCategoryForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from datetime import datetime
from django.contrib import messages
from utils.pagination import paginate
from utils.functional import combine_dicts
from django.http import HttpResponse
import json

def bookmarks(request, username, category_id = None):
    
    user = get_object_or_404(User, username__iexact=username)
    is_owner = request.user.is_authenticated and user == request.user
    
    '''
    if is_owner and request.POST and "create_cat" in request.POST:
        form_bookmark_category = BookmarkCategoryForm(request.POST, instance=BookmarkCategory(user=user))
        if form_bookmark_category.is_valid():
            form_bookmark_category.save()
        
        form_bookmark_category = BookmarkCategoryForm()
        
    form_bookmark_category = BookmarkCategoryForm()
    '''    
    
    n_uncat = Bookmark.objects.select_related("sound").filter(user=user,category=None).count()
    
    if not category_id:
        bookmarked_sounds = Bookmark.objects.select_related("sound").filter(user=user,category=None)
    else:
        category = get_object_or_404(BookmarkCategory,id=category_id,user=user)
        bookmarked_sounds = category.bookmarks.select_related("sound").all()
    
    bookmark_categories = BookmarkCategory.objects.filter(user=user)
    
    return render_to_response('bookmarks/bookmarks.html', combine_dicts(locals(),paginate(request, bookmarked_sounds, 30)), context_instance=RequestContext(request))

@login_required
def delete_bookmark_category(request, category_id):
    
    category = get_object_or_404(BookmarkCategory,id=category_id, user=request.user)
    msg = "Deleted bookmark category \"" + category.name + "\"."
    category.delete()
    messages.add_message(request, messages.WARNING, msg)
    
    next = request.GET.get("next","")
    if next:
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect(reverse("bookmarks-for-user", args=[request.user.username]))

@login_required
def add_bookmark(request, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)
    
    if request.POST:
        category_id = int(request.POST["categories_list"])
        category_name = request.POST["cat_name"]
        name = request.POST["name"]
    else:
        category_id = -1
        name = ""
        category_name = ""
    
    if category_id == -1: # nothing todo with categories
        category = False
    elif category_id == -2: # create new category
        category = BookmarkCategory(user=request.user, name=category_name)
        category.save()
    else: # get existing category from id
        category = get_object_or_404(BookmarkCategory,id=category_id)

    bookmark = Bookmark(user=request.user,sound=sound)
    bookmark.name = name
    if category:
        bookmark.category = category
    bookmark.save()
     
    if request.is_ajax():
        return HttpResponse()   
    else:
        
        msg = "Added new bookmark for sound \"" + sound.original_filename + "\"."
        messages.add_message(request, messages.WARNING, msg)
    
        next = request.GET.get("next","")
        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect(reverse("sound", args=[sound.user.username, sound.id]))


@login_required
def delete_bookmark(request, bookmark_id):
    
    bookmark = get_object_or_404(Bookmark,id=bookmark_id, user=request.user)
    msg = "Deleted bookmark for sound \"" + bookmark.sound.original_filename + "\"."
    bookmark.delete()
    messages.add_message(request, messages.WARNING, msg)
    
    next = request.GET.get("next","")
    if next:
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect(reverse("bookmarks-for-user", args=[request.user.username]))

@login_required       
def get_form_for_sound(request, sound_id):
    
    sound = Sound.objects.get(id=sound_id)
    categories = BookmarkCategory.objects.filter(user=request.user)
    bookmarks = Bookmark.objects.filter(user=request.user,sound=sound)
    categories_aready_containing_sound = BookmarkCategory.objects.filter(user=request.user, bookmarks__sound=sound).distinct()
    
    data_dict = {'request_user_username':request.user.username,
                 'bookmarks': bookmarks.count() != 0,
                 'sound_id':sound.id,
                 'sound_name':sound.original_filename,
                 'categories_aready_containing_sound':categories_aready_containing_sound,
                 'categories':categories,}
    
    template = 'bookmarks/bookmark_form.html'
    
    return render_to_response(template, data_dict, context_instance = RequestContext(request))
    