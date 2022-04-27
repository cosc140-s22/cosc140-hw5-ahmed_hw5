from django import forms

class ProductFilterForm(forms.Form):
    name_search = forms.CharField(label="Name search", max_length=50, required=False)
    min_price = forms.DecimalField(decimal_places=2, min_value=0, required=False)
    max_price = forms.DecimalField(decimal_places=2, min_value=0, required=False)
