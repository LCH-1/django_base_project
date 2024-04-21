from django import forms


class OrderForm(forms.ModelForm):
    order = forms.ChoiceField(label="order", choices=(), required=True)
    is_order_form = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.instance._meta.model
        dynamic_choices = list(self.model.objects.order_by("order").values_list('order', flat=True))
        dynamic_choices = [(x, i) for i, x in enumerate(dynamic_choices, 1)]

        if dynamic_choices:
            last_order = tuple(x+1 for x in dynamic_choices[-1])
        else:
            last_order = (1, 1)
        # dynamic_choices = list(self.model.objects.order_by("-order").values_list('order', 'order'))
        # last_order = dynamic_choices[0][0] + 1

        if not self.instance.pk:
            dynamic_choices.append(last_order)
            # dynamic_choices.insert(0, (last_order, last_order))
            self.fields['order'].choices = dynamic_choices
            self.fields['order'].initial = last_order

        else:
            self.fields['order'].choices = dynamic_choices
