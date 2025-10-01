from django import forms


from .models import ScamReport

class LinkCheckForm(forms.Form):
    url = forms.URLField(
        label="",
        widget=forms.URLInput(attrs={
            "class": "w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:outline-none",
            "placeholder": "Enter a URL (e.g. https://example.com)"
        })
    )



class ScamReportForm(forms.ModelForm):
    class Meta:
        model = ScamReport
        fields = [
            'initiative_type',
            'whatsapp',
            'facebook',
            'email',
            'other',
            'reference',
            'screenshots',
            'description',
            'contact',
        ]
        widgets = {
            'initiative_type': forms.Select(attrs={'class': 'form-select w-full'}),
            'reference': forms.TextInput(attrs={'class': 'form-input w-full', 'placeholder': 'Paste Link / Reference Code'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea w-full', 'placeholder': 'What made you suspicious?'}),
            'contact': forms.TextInput(attrs={'class': 'form-input w-full', 'placeholder': 'Email or Phone (Optional)'}),
        }