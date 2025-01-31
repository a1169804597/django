from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='用户名或邮箱',
                               widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户名或者邮箱'}))
    password = forms.CharField(label='密码', 
                               widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码'}))

    def clean(self):
        username_or_email=self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        username=''
        if  not User.objects.filter(username=username_or_email):
            if User.objects.filter(email=username_or_email):
                username = User.objects.get(email=username_or_email).username
        else:
            username = username_or_email
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data

class RegForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=30,
                               min_length=3,
                               widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入3-30位用户名'}))
    email = forms.EmailField(label='邮箱', 
                             widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'请输入邮箱'}))
    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    password = forms.CharField(label='密码', 
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码'}))
    password_again = forms.CharField(label='再输入一次密码', 
                                     min_length=6,
                                     widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'再输入一次密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again

    def clean_verification_code(self):
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label='新的昵称',
                                max_length=20,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}))
    def __init__(self,*args,**kwargs):
        if 'user' in kwargs:
            self.user=kwargs.pop('user')
            super().__init__(*args,**kwargs)
    def clean(self):
        if  self.user.is_authenticated:
            self.cleaned_data['user']=self.user
        else:
            raise forms.ValidationError('用户未登入')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new','').strip()
        if nickname_new =='':
            raise forms.ValidationError('昵称不能为空')
        return nickname_new

class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮件',
                               widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'}))
    verification_code = forms.CharField(label='验证码',required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    def __init__(self,*args,**kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args,**kwargs)

    def clean(self):
        if self.request.user.is_authenticated:
            self.cleaned_data['user']=self.request.user
        else:
            raise forms.ValidationError('用户未登入')
        if not self.request.user.email=='':
            raise forms.ValidationError('你已经绑定邮箱了')

        code = self.request.session.get('bind_email_code','')
        verification_code=self.cleaned_data.get('bind_code','')
        if not (code !='' and code==verification_code ):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email=self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定了')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code','').strip()
        print('验证码为%s'%verification_code)
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入旧密码'}))
    new_password =  forms.CharField(label='新密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输新入密码'}))
    new_password_again = forms.CharField(label='重复新密码',
                               min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请重复输入新密码'}))

    def __init__(self,*args,**kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args,**kwargs)

    def clean(self):
        # 是否登入
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        import pdb
        pdb.set_trace()
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        #验证旧密码是否正确
        old_password = self.cleaned_data.get('old_password','')
        if not self.request.user.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        return old_password

class ForgotPasswordForm(forms.Form):
    email=forms.EmailField(label='邮箱',
                           widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'请输入邮箱地址'}))
    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    new_password = forms.CharField(label='新密码',
                                   min_length=6,
                                   widget=forms.PasswordInput(
                                       attrs={'class': 'form-control', 'placeholder': '请输新入密码'}))
    new_password_again = forms.CharField(label='重复新密码',
                                         min_length=6,
                                         widget=forms.PasswordInput(
                                             attrs={'class': 'form-control', 'placeholder': '请重复输入新密码'}))
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        #判断邮箱是否存在
        email=self.cleaned_data.get('email','')
        if not User.objects.filter(email=email):
            raise forms.ValidationErrot('输入的邮箱不存在')
        #验证码是否正确
        code = self.request.session.get('forgot_email_code', '')
        verification_code = self.cleaned_data.get('bind_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_new_password(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        import pdb
        pdb.set_trace()
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        print('验证码为%s' % verification_code)
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

