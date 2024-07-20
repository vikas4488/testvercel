from .models import Flowers,Favorits,Cart,Category,Subcategory
def allcatagories(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return {'categories': categories}
def getcartCount(request):
    if request.user.is_authenticated:
        cartcount = Cart.objects.filter(userob_id=request.user.id).count()
    else:
        cartcount = 0
    return {'cartcount': cartcount}
def getlikeCount(request):
    if request.user.is_authenticated:
        likecount = Favorits.objects.filter(userob_id=request.user.id).count()
    else:
        likecount = 0
    return {'likecount': likecount}