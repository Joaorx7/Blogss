from django import forms
from .models import Post, Comentario, Categoria, Mensagem, Perfil  # ← Certifique-se de importar Categoria
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'conteudo', 'categoria', 'imagem']  # ← Adicionado 'imagem'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['conteudo', 'resposta_a']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escreva um comentário...'}),
            'resposta_a': forms.HiddenInput()
        }


class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ['conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escreva sua mensagem...'})
        }

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email