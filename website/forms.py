from django import forms

class LinkCheckForm(forms.Form):
    url = forms.URLField(
        label="",
        widget=forms.URLInput(attrs={
            "class": "w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:outline-none",
            "placeholder": "Enter a URL (e.g. https://example.com)"
        })
    )
