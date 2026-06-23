from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Resource

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ResourceForm(forms.ModelForm):
    """Form for creating and editing resources"""
    
    class Meta:
        model = Resource
        fields = ['name', 'description', 'location', 'max_capacity', 'price_per_hour', 'image', 'image_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your resource...'}),
            'location': forms.TextInput(attrs={'placeholder': 'Where is this resource located?'}),
            'max_capacity': forms.NumberInput(attrs={'min': 1, 'placeholder': '1'}),
            'price_per_hour': forms.NumberInput(attrs={'min': 0, 'step': 0.01, 'placeholder': '0.00'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['name', 'description']:
                field.required = False
            if field_name == 'image':
                field.help_text = "Upload an image file (JPG, PNG, GIF). Max 5MB."
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        if image:
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f"Unsupported file extension. Please use: {', '.join(valid_extensions)}")
        return image

class ResourceStatusForm(forms.ModelForm):
    """Form for admins to update resource status"""
    
    class Meta:
        model = Resource
        fields = ['status']