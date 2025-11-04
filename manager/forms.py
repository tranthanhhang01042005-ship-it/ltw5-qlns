from django import forms
from lalinapp.models import Profile,Complaint, Topic
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['start_date', 'end_date', 'user', 'status', 'salary']
        widgets = {'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                   'address': forms.TextInput(attrs={'class': 'form-control'}),
                   'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                   'image': forms.FileInput(attrs={'type': 'file', 'class': 'form-control'}),
                   'cccd': forms.TextInput(attrs={'class': 'form-control'}),
                   'major': forms.TextInput(attrs={'class': 'form-control'}),
                   'degree': forms.Select(attrs={'class': 'form-select'}),
                   'gender': forms.Select(attrs={'class': 'form-select'}),
                   'position': forms.Select(attrs={'class': 'form-select'}),
                   'contract_period': forms.TextInput(attrs={'class': 'form-control'}), }
        labels = {'dob': 'Ngày sinh', 'address': 'Địa chỉ', 'phone_number': 'Số điện thoại',
                  'image': 'Ảnh profile', 'cccd': 'Căn cước công dân', 'major': 'Chuyên ngành',
                  'degree': 'Bằng cấp', 'gender': 'Giới tính', 'position': 'Chức vụ',
                  'contract_period': 'Thời hạn hợp đồng'}


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'email': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'first_name': 'Họ', 'last_name': 'Tên', 'email': 'Email'}


class EmployeeCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'}),
                   'email': forms.TextInput(attrs={'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'username': 'Tên đăng nhập', 'email': 'Email', 'first_name': 'Họ', 'last_name': 'Tên'}
        help_texts = {'username': ''}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password1'].help_text = ''
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].label = 'Nhập lại mật khẩu'
        self.fields['password2'].help_text = ''