from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.auth.models import User

# Register your models here.
from .models import Order, Item

admin.site.register(Item)

class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/cart/order/change_list.html'

    def get_urls(self):
        return [
            path(
                'statistics/',
                self.admin_site.admin_view(self.statistics_view),
                name='cart_order_statistics'
            ),
        ] + super().get_urls()

    def statistics_view(self, request):
        top_buyer = (
            User.objects.annotate(movies_purchased=Sum('order__item__quantity'))
            .filter(movies_purchased__gt=0)
            .order_by('-movies_purchased', 'username', 'pk')
            .first()
        )

        context = {
            **self.admin_site.each_context(request),
            'title': 'Order Statistics',
            'top_buyer': top_buyer,
        }

        return TemplateResponse(
            request,
            'admin/cart/order/statistics.html',
            context
        )

admin.site.register(Order, OrderAdmin)