from django import forms
from django.contrib.auth.models import User


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

