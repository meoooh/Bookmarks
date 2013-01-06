# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.http import HttpResponse, Http404
#from django.template import Context
#from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from bookmarks.forms import *
from bookmarks.models import *

from django.contrib.auth.decorators import login_required

def main_page(request):
#	template = get_template('main_page.html')
#	variables = Context({
#			'head_title':'장고 북마크',
#			'page_title':'장고 북마크에 오신 것을 환영합니다.',
#			'page_body': '북마크를 저장하고 공유하세요!',
#			'user':request.user,
#			})
#	output = template.render(variables)
#	return HttpResponse(output)
#	return render_to_response(
#			'main_page.html',
#			{'user':request.user,
#			'head_title':'장고 북마크',
#			'page_title':'장고 북마크에 오신 것을 환영합니다.',
#			'page_body':'북마크를 저장하고 공유하세요!',
#			})
	shared_bookmarks = SharedBookmark.objects.order_by(
			'-date'
			)[:10]
	variables = RequestContext(request, {
			'user':request.user,
			'head_title':'장고 북마크',
			'page_title':'장고 북마크에 오신 것을 환영합니다.',
			'page_body':'북마크를 저장하고 공유하세요!',
			'shared_bookmarks':shared_bookmarks,
			})
	return render_to_response('main_page.html', variables)

def user_page(request, username):
	"""
	try:
		user = User.objects.get(username=username)
	except:
		raise Http404('사용자를 찾을 수 없습니다.')
	"""#쉽고 빠른 웹개발 5.2.3에서 대체됨

	#bookmarks = user.bookmark_set.all()
	user = get_object_or_404(User, username=username)
	bookmarks = user.bookmark_set.order_by('-id')

#	template = get_template('user_page.html')
#	variables = Context({
#			'username':username,
#			'bookmarks':bookmarks
#			})
#	output = template.render(variables)
#	return HttpResponse(output)
#	return render_to_response(
#			'user_page.html',
#			{'username':username,
#			'bookmarks':bookmarks,
#			})
	variables = RequestContext(request, {
			'username':username,
			'bookmarks':bookmarks,
			'show_tags':True,
			'show_edit': username == request.user.username,
#			'show_edit': True,
			})
	return render_to_response('user_page.html', variables)

def logout_page(request):
	logout(request)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def register_page(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
					username=form.cleaned_data['username'],
					password=form.cleaned_data['password1'],
					email=form.cleaned_data['email']
					)
			return HttpResponseRedirect('/register/success')
	#	else:
	#		variables = RequestContext(request, {'form':form})
	#		return render_to_response('registration/register.html',
	#				variables)
	else:
		form = RegistrationForm()

	variables = RequestContext(request, {
				'form': form
				})
	return render_to_response('registration/register.html',
			variables)

@login_required# 데코레이터, 쉽고 빠른 웹 개발 5.2.1 참조
def user_modification_page(request):
	if request.method == 'POST':
		form = PasswordModificationForm(request.user, request.POST)
		if form.is_valid():
			if form.cleaned_data['newPassword2']:
				request.user.set_password(form.cleaned_data['newPassword2'])
				request.user.save()
			return HttpResponseRedirect('/logout/')
	elif request.method == 'GET':
#	  	if not request.user.is_authenticated(): # 데코레이터를 상단에 추가했으니 거기서 로그인 여부 검사해줌
#			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#			return HttpResponseRedirect('/')
		form = PasswordModificationForm()
	else:
		raise Http404('views.py.user_modification_page method error else statement')

	variables = RequestContext(request, {
			'form':form
			})
	return render_to_response('user_modification.html',
			variables)

@login_required # 데코레이터, 쉽고 빠른 웹 개발 5.2.1 참조
def bookmark_save_page(request):
	ajax = request.GET.has_key('ajax')
	if request.method == 'POST':
		form = BookmarkSaveForm(request.POST)
		if form.is_valid():
			bookmark = _bookmark_save(request, form)
#			import pdb
#			pdb.set_trace()
			if ajax:
				variables = RequestContext(request, {
						'bookmarks':[bookmark],
						'show_edit':True,
						'show_tags':True,
						})
				return render_to_response('bookmark_list.html', 
						variables)
			else:
				return HttpResponseRedirect(
						'/user/%s/'%request.user
					)
		else:
			if ajax:
				return HttpResponse('failure')
	elif request.GET.has_key('url'):
		url = request.GET['url']
		title=''
		tags=''
		share=True
		try:
			link = Link.objects.get(url=url)
			bookmark = Bookmark.objects.get(
					link=link,
					user=request.user,
					)
			title = bookmark.title
			tags = ' '.join(
					tag.name for tag in bookmark.tag_set.all()
					)
			SharedBookmark.objects.get(
					bookmark=bookmark
					)
		except ObjectDoesNotExist:
			share=False
		form = BookmarkSaveForm({
				'url':url,
				'title':title,
				'tags':tags,
				'share':share,
				})
	else:
		form = BookmarkSaveForm()

	variables = RequestContext(request, {
			'form':form
			})

	if ajax:
		return render_to_response(
				'bookmark_save_form.html',
				variables,
				)
	else:
		return render_to_response('bookmark_save.html', variables)

def tag_page(request, tag_name):
	tag = get_object_or_404(Tag, name=tag_name)
	bookmarks = tag.bookmarks.order_by('-id')
	variables = RequestContext(request, {
			'bookmarks':bookmarks,
			'tag_name':tag_name,
			'show_tags':True,
			'show_user':True,
			})
	return render_to_response('tag_page.html', variables)

def tag_cloud_page(request):
	MAX_WEIGHT = 5
	tags = Tag.objects.order_by('name')

	# Calculate tag, minand max counts.
	min_count = max_count = tags[0].bookmarks.count()
	for tag in tags:
		tag.count = tag.bookmarks.count()
		if tag.count < min_count:
			min_count = tag.count
		if tag.count > max_count:
			max_count = tag.count
	
	# Calculate count range. Avoid dividing by zero.
	_range = float(max_count - min_count)
	if _range == 0.0:
		_range = 1.0

	# Calculate tag weights.
	for tag in tags:
		tag.weight = int(
				MAX_WEIGHT * (tag.count - min_count) / _range
				)

	variables = RequestContext(request, {
			'tags':tags
			})
	
	return render_to_response('tag_cloud_page.html',
			variables,)

def search_page(request):
	form = SearchForm()
	bookmarks = []
	show_results = False
	if request.GET.has_key('query'):
#	if query:
		show_results = True
		query = request.GET['query'].strip()
		if query:
			form = SearchForm({'query':query})
			bookmarks = \
				Bookmark.objects.filter(title__icontains=query)[:10]
	
	variables = RequestContext(request, {
			'form':form,
			'bookmarks':bookmarks,
			'show_results':show_results,
			'show_tags':True,
			'show_user':True,
			})
#	import pdb
#	pdb.set_trace()
	if request.is_ajax():
		return render_to_response('bookmark_list.html', variables)
	else:
		return render_to_response('search.html', variables)

def _bookmark_save(request, form):
	link, dummy = Link.objects.get_or_create(
			url=form.cleaned_data['url'],
			)   
	# 북마크가 있으면 가져오고 없으면 새로 저장합니다.
	bookmark, created = Bookmark.objects.get_or_create(
			user=request.user,
			link=link,
			) 

	# 북마크 제목을 수정합니다.
	bookmark.title = form.cleaned_data['title']

	# 북마크를 수정한 경우에는 이전에 입력된 모든 태그를 지웁니다.
	if not created:
		bookmark.tag_set.clear()

	# 태그 목록을 새로 만듭니다.
	tag_names = form.cleaned_data['tags'].split()
	for tag_name in tag_names:
		tag, dummy = Tag.objects.get_or_create(name=tag_name)
		bookmark.tag_set.add(tag)

#	import pdb
#	pdb.set_trace()
	if form.cleaned_data['share']:
		shared_bookmark, created = SharedBookmark.objects.get_or_create(
					bookmark=bookmark
				)
		if created:
			shared_bookmark.users_voted.add(request.user)
			shared_bookmark.save()
	else:
		try:
			SharedBookmark.objects.get(bookmark=bookmark).delete()
		except ObjectDoesNotExist:
			pass

	# 북마크를 저장합니다.
	bookmark.save()
	return bookmark

def ajax_tag_autocomplete(request):
	if request.GET.has_key('q'):
		tags=Tag.objects.filter(name__istartswith=request.GET['q'])
		
		return HttpResponse('\n'.join(tag.name for tag in tags))
	return HttpResponse()

@login_required
def bookmark_vote_page(request):
	if request.GET.has_key('id'):
		try:
			id = request.GET['id']
			shared_bookmark = SharedBookmark.objects.get(id=id)
			user_voted = shared_bookmark.users_voted.filter(
					username=request.user.username
					)
#			import pdb
#			pdb.set_trace()
			if not user_voted:
				shared_bookmark.votes += 1
				shared_bookmark.users_voted.add(request.user)
				shared_bookmark.save()
		except ObjectDoesNotExist:
			raise Http404('북마크를 찾을 수 없습니다.')

	if request.META.has_key('HTTP_REFERER'):
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	
	return HttpResponseRedirect('/')

from datetime import datetime, timedelta

def popular_page(request):
	today = datetime.today()
	yesterday = today - timedelta(1)
	shared_bookmarks = SharedBookmark.objects.filter(
			date__gt = yesterday
			)
	shared_bookmarks = shared_bookmarks.order_by(
			'-votes'
			)[:10]
	variables = RequestContext(request, {
			'shared_bookmarks':shared_bookmarks
			})
	return render_to_response('popular_page.html',
			variables)

def bookmark_page(request, bookmark_id):
	shared_bookmark = get_object_or_404(
		SharedBookmark,
		id=bookmark_id,
		)
	variables = RequestContext(request, {
		'shared_bookmark': shared_bookmark,
		})
	return render_to_response('bookmark_page.html',
		variables)
