from django import forms
from .models import Fazenda  

class FazendaForm(forms.ModelForm):
    class Meta:
        model = Fazenda  # Modelo vinculado ao form
        fields = '__all__'  # Usa TODOS os campos do modelo
        
        # Opcional: Personalizar como os campos aparecem
        widgets = {
            'data_de_cadastro': forms.DateInput(attrs={
                'type': 'date',  # Transforma em campo de data HTML5
                'class': 'form-control'  # Classe CSS (opcional)
            }),
            'localizacao': forms.Textarea(attrs={
                'rows': 3,  # Textarea com 3 linhas
                'placeholder': 'Digite o endereço completo'
            })
        }