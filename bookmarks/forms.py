# -*- coding: utf-8 -*-

import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import forms

class RegistrationForm(forms.Form):
	username = forms.CharField(label='사용자 이름', max_length=30)
	email = forms.EmailField(label='전자우편')
	password1 = forms.CharField(
			label='비밀번호',
			widget=forms.PasswordInput()
			)
	password2 = forms.CharField(
			label='비밀번호(확인용)',
			widget=forms.PasswordInput()
			)

	def clean_password2(self):
		if 'password1' in self.cleaned_data:
			password1 = self.cleaned_data['password1']
			password2 = self.cleaned_data['password2']
			if password1 == password2:
				return password1
		raise forms.ValidationError('비밀번호가 일치하지 않습니다.')

	def clean_username(self):
		username = self.cleaned_data['username']
#		if not re.search(r'^\w+$', username):
#			raise forms.ValidationError(
#					'사용자 이름은 알파벳, 숫자, 밑줄(_)만 가능합니다.')
		try:
			User.objects.get(username=username)
		except ObjectDoesNotExist:
			return username
		raise forms.ValidationError('이미 사용 중인 사용자 이름입니다.')

class PasswordModificationForm(forms.Form):
	currentPassword = forms.CharField(
			label='현재 비밀번호',
			widget=forms.PasswordInput(),
			)
	newPassword1 = forms.CharField(
			label='새로운 비밀번호',
			widget=forms.PasswordInput(),
			required=False,
			)
	newPassword2 = forms.CharField(
			label='새로운 비밀번호(확인용)',
			widget=forms.PasswordInput(),
			required=False,
			)

	def __init__(self, user=None, *args):
		self.user = user
		super(PasswordModificationForm, self).__init__(*args)
	
	def clean_currentPassword(self):
		if not self.user.check_password(self.cleaned_data['currentPassword']):
			raise forms.ValidationError('현재 비밀번호가 일치하지 않습니다.')

	def clean_newPassword2(self):
		if 'newPassword1' in self.cleaned_data:
			newPassword1 = self.cleaned_data['newPassword1']
			newPassword2 = self.cleaned_data['newPassword2']
			if newPassword1 == newPassword2:
				return newPassword2
			elif newPassword1 != newPassword2:
				raise forms.ValidationError('새로운 비밀번호가 일치하지 않습니다.')

class SearchForm(forms.Form):
	query = forms.CharField(
			label='검색어를 입력하세요.',
			widget=forms.TextInput(attrs={'size':32})
			)

class BookmarkSaveForm(forms.Form):
	url=forms.URLField(
				label='주소',
				widget=forms.TextInput(attrs={'size':64}),
			)
	title = forms.CharField(
				label='제목',
				widget=forms.TextInput(attrs={'size':64}),
			)
	tags = forms.CharField(
				label='태그',
				required=False,
				widget=forms.TextInput(attrs={'size':64}),
			)
	share = forms.BooleanField(
				label='첫 페이지에서 공유합니다.',
				required=False
			)
	"""
	def clean_share(self):
		import pdb
		pdb.set_trace()
		if self.cleaned_data['share'] == 'checked':
			return True
		else:
			return False
	"""
