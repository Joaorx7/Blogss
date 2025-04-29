from django import forms
from .models import Post, Comentario, Categoria, Perfil
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

#Contém classes baseadas em ModelForm ou Form que definem os formulários usados nas views (ex: PostForm, ComentarioForm).

# Formulário de cadastro de usuário com campo de e-mail obrigatório
class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Formulário para criação e edição de posts
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'conteudo', 'categoria', 'imagem']
        widgets = {
            'conteudo': forms.Textarea(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o título aqui'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].required = True  # Garante que a categoria seja obrigatória

# Formulário para criação de comentários e respostas
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['conteudo', 'resposta_a']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escreva um comentário...'}),
            'resposta_a': forms.HiddenInput()  # Campo oculto usado para referenciar respostas
        }

# Formulário para edição do perfil do usuário (bio)
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

# Versão personalizada do formulário de criação de usuário com validação de e-mail único
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")  # Gera erro se o e-mail já estiver cadastrado
        return email
