# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User

#User registration form
class RegistrationForm(forms.Form):
	
	user = forms.CharField(max_length=30,required=True)
	
	email_id = forms.EmailField(required=True)
	
	password1 = forms.PasswordInput()

	password2 = forms.PasswordInput()


	def isValidUsername(self):
		try:
			User.objects.get(username=self.cleaned_data['user'])
		except User.DoesNotExist:
			return False

		return True


	def validity(self):
		return self.cleaned_data['password1'] == self.cleaned_data['password2']  


	def save(self):
		new_user = User.objects.create_user(username=self.data['user'],email=self.data['email_id'],password=self.data['password1'])			

		# new_user.is_active = False
		new_user.save()

		return new_user 


#Lost password form
class LostPasswordForm(forms.Form):
	username = forms.CharField(label="Username", max_length=30)
	email = forms.EmailField(label="E-mail")

	def clean_username(self):
		# clean old keys when it's requested
		old_keys = LostPassword.objects.filter(key_expires__lt=datetime.date.today())
		for key in old_keys: key.delete()

		field_data = self.cleaned_data['username']

		# control username whether it exists or not
		if len(User.objects.filter(username__iexact=field_data)) == 0:
			raise forms.ValidationError("This username is not registered")

		# control if this user has requested a new password
		if len(LostPassword.objects.filter(user__username__iexact=field_data)) > 0:
			raise forms.ValidationError("This username has already requested a new password")

		return field_data

	def clean_email(self):
		field_data = self.cleaned_data['email']

		if not self.cleaned_data.has_key('username'):
			return
		else:
			username = self.cleaned_data['username']

		# control email if it is correct
		try:
			u = User.objects.get(username=username)
			if u.email != field_data:
				raise forms.ValidationError("This e-mail address is not registered")
		except User.DoesNotExist:
			pass

		return field_data


#Change password form
class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(label="Old password", widget=forms.PasswordInput)
	password = forms.CharField(label="Password", widget=forms.PasswordInput)
	password_again = forms.CharField(label="Password (Again)", widget=forms.PasswordInput)

	def set_user(self, user):
		self.user = user

	def clean_old_password(self):
		field_data = self.cleaned_data['old_password']

		if len(field_data.split(' ')) != 1:
			raise forms.ValidationError("Password may not contain space character")

		if len(field_data) > 32:
			raise forms.ValidationError("Password must contain less than 32 characters")

		if len(field_data) < 5:
			raise forms.ValidationError("Password must be at least 5 characters long")

		return field_data

	def clean_password(self):
		field_data = self.cleaned_data['password']

		if len(field_data.split(' ')) != 1:
			raise forms.ValidationError("Password may not contain space character")

		if len(field_data) > 32:
			raise forms.ValidationError("Password must contain less than 32 characters")

		if len(field_data) < 5:
			raise forms.ValidationError("Password must be at least 5 characters long")

		return field_data

	def clean_password_again(self):
		field_data = self.cleaned_data['password_again']

		if not self.cleaned_data.has_key('password') or not self.cleaned_data.has_key('old_password'):
			return
		else:
			password = self.cleaned_data['password']
			old_password = self.cleaned_data['old_password']

		if old_password or password or field_data:
			if field_data and password and old_password:
				if len(field_data.split(' ')) != 1:
					raise forms.ValidationError("Password may not contain space character")

			if len(field_data) > 32:
				raise forms.ValidationError("Password must contain less than 32 characters")

			if len(field_data) < 5:
				raise forms.ValidationError("Password must be at least 5 characters long")

			if (password or field_data) and password != field_data:
				raise forms.ValidationError("Passwords don't match")

			u = User.objects.get(username=self.user.username)
			if not u.check_password(old_password):
				raise forms.ValidationError("Old password is wrong")

			return field_data
		else:
			raise forms.ValidationError("Fill all of the fields to change password")
        
		return ''


#Reset password form
class ResetPasswordForm(forms.Form):
	password = forms.CharField(label="Password", widget=forms.PasswordInput, max_length=32, min_length=5)
	password_again = forms.CharField(label="Password (Again)", widget=forms.PasswordInput, max_length=32, min_length=5)

	def clean_password_again(self):
		field_data = self.cleaned_data['password_again']

		if not self.cleaned_data.has_key('password'):
			return
		else:
			password = self.cleaned_data['password']

		if field_data != password:
			raise forms.ValidationError("Passwords don't match")

		return field_data
