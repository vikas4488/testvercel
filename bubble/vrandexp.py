from django.db.models import F, ExpressionWrapper, DecimalField,Sum,Q
from .helper import Round
from .models import Favorits,Cart
from django.db.models import OuterRef,Exists,When,Value,Case,CharField
from django.db.models import F, ExpressionWrapper, DecimalField

newPriceExpression = ExpressionWrapper(
                Round(F('price') * (1 - F('offvalue') / 100), 2),
                output_field=DecimalField(max_digits=10, decimal_places=2)
                )
def isCarted(userid):
    cart_subquery=Cart.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
    return Case(When(Exists(cart_subquery),
                        then=Value("carted")),default=Value("not_carted"),output_field=CharField())
def isFavorite(userid):
    fav_subquery=Favorits.objects.filter(userob_id=userid,flowerob_id=OuterRef('pk'))
    return Case(When(Exists(fav_subquery),
                    then=Value("liked")),default=Value("not_liked"),output_field=CharField())