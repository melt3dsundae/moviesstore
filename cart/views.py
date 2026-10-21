from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Initialize the geocoder with a unique user agent
geolocator = Nominatim(user_agent="moviesstore")

def geocode(city):
    print(f"Geocoding city: {city}")
    if not city:
        print("No city provided")
        return None
    try:
        location = geolocator.geocode(city)
        if location:
            address = location.raw["display_name"]
            print(f"Address: {location.address}")
            print(f"Coordinates: {location.latitude}, {location.longitude}")
            return address, location.latitude, location.longitude
        else:
            print("Address not found")
            return None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error: {e}")
        return None

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    result = geocode(request.POST.get('city', '').strip())
    if result:
        order.region, order.region_lat, order.region_lng = result
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html', {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html', {'template_data': template_data})

@login_required
def popularity_map(request):
    template_data = {}
    template_data['title'] = 'Popularity Map'
    # get trending movies per region
    regions = {}
    for item in Item.objects.select_related('order', 'movie'):
        o = item.order
        r = regions.setdefault(o.region, {'region': o.region, 'lat': o.region_lat, 'lng': o.region_lng, 'counts': {}})
        r['counts'][item.movie.name] = r['counts'].get(item.movie.name, 0) + item.quantity
    for r in regions.values():
        r['counts'] = dict(list(sorted(r['counts'].items(), key=lambda x: x[1], reverse=True))[:5])
    template_data['regions'] = list(regions.values())
    return render(request, 'cart/map.html', {'template_data': template_data})