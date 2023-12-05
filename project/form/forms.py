from django import forms

class DonutForm(forms.Form):
    ndvi = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": 'form-control',
                "id":"ndvi-file"
            }
        ),
        label="1. Upload UAV Images (TIFF or JPG)"
    )
    shape = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": 'form-control',
                "id":"shape-file"
            }
        ),
        label="2. Upload Shapefile"
    )
    buffer = forms.FloatField(
        widget=forms.TextInput(
            attrs={
                "class": 'form-control',
                "id":"buffer-distance",
                "placeholder":"3 < buffer <= 8"
            },
        ),
        label="3. Buffer Distance"
    )