from django import forms


class BookmarkSaveForm(forms.Form):
    url = forms.URLField(
        label='URL',
        widget=forms.TextInput(attrs={'size': 64}))
    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(attrs={'size': 64}))
    tags = forms.CharField(
        label='Tags',
        required=False,
        widget=forms.TextInput(attrs={'size': 64}))
    share = forms.BooleanField(
        label='Share on the main page',
        required=False)


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Enter a keyword to search for',
        widget=forms.TextInput(attrs={'size': 32})
    )
