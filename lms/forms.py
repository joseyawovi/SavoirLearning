"""
Forms for Savoir+ LMS.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Roadmap, Room, Section, Question


class UserRegistrationForm(UserCreationForm):
    """User registration form with additional fields."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': _('Email address')
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('First name')
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Last name')
    }))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Username')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm password')
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class QuizAnswerForm(forms.Form):
    """Form for quiz answer submission."""
    answer = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your answer...')
        }),
        label=_('Your Answer')
    )


class RoadmapForm(forms.ModelForm):
    """Form for creating and editing roadmaps."""
    class Meta:
        model = Roadmap
        fields = ['title', 'title_fr', 'description', 'description_fr', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter roadmap title...')
            }),
            'title_fr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter French title...')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Enter roadmap description...')
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Enter French description...')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class RoomForm(forms.ModelForm):
    """Form for creating and editing rooms."""
    class Meta:
        model = Room
        fields = ['title', 'title_fr', 'description', 'description_fr', 'roadmap', 'prerequisite_room', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter room title...')
            }),
            'title_fr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter French title...')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Enter room description...')
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Enter French description...')
            }),
            'roadmap': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prerequisite_room': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter prerequisite rooms to only show rooms from the same roadmap
        if 'roadmap' in self.data:
            try:
                roadmap_id = int(self.data.get('roadmap'))
                self.fields['prerequisite_room'].queryset = Room.objects.filter(roadmap_id=roadmap_id, is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.roadmap:
            self.fields['prerequisite_room'].queryset = Room.objects.filter(
                roadmap=self.instance.roadmap, is_active=True
            ).exclude(pk=self.instance.pk)


class SectionForm(forms.ModelForm):
    """Form for creating and editing sections."""
    class Meta:
        model = Section
        fields = ['room', 'title', 'title_fr', 'content', 'content_fr', 'video_url', 'order', 'is_active']
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter section title...')
            }),
            'title_fr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter French title...')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('Enter section content... (HTML supported)')
            }),
            'content_fr': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': _('Enter French content... (HTML supported)')
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter video URL (optional)...')
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions."""
    class Meta:
        model = Question
        fields = ['section', 'room', 'question_type', 'prompt', 'prompt_fr', 'correct_answer', 'placeholder_hint', 'order', 'is_active']
        widgets = {
            'section': forms.Select(attrs={
                'class': 'form-control'
            }),
            'room': forms.Select(attrs={
                'class': 'form-control'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prompt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Enter question prompt...')
            }),
            'prompt_fr': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Enter French prompt...')
            }),
            'correct_answer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter correct answer...')
            }),
            'placeholder_hint': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter placeholder hint (e.g., "_____ _____")...')
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Conditional field requirements based on question type
        question_type = self.data.get('question_type') or (self.instance.question_type if self.instance.pk else None)
        
        if question_type == 'section':
            self.fields['room'].required = False
            self.fields['section'].required = True
        elif question_type == 'final':
            self.fields['section'].required = False
            self.fields['room'].required = True


class UserEditForm(forms.ModelForm):
    """Form for editing user details by admin."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_paid_user', 'trial_end_date', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'trial_end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_paid_user': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
