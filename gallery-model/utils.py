from functools import wraps

from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest

from gallery.models import User


def check_auth(function):
    @wraps(function)
    def wrapper(request: HttpRequest, *args, **kwargs):
        session = request.COOKIES.get("session")

        try:
            user = User.objects.get(session=session)
            user_id = user.id
            username = user.username
        except:
            return HttpResponseRedirect("/login")
        
        return function(
                request=request, 
                user_id=user_id, 
                name=username, 
                *args, **kwargs
            )
        
    return wrapper


def check_query_set_for_getting_data(function):
    wraps(function)
    def wrapper(request: HttpRequest, *args, **kwargs):
        try:
            skip = request.GET.get("skip") or 0
            limit = request.GET.get("limit") or 5
            skip = int(skip)
            limit = int(limit)
        except:
            return HttpResponseBadRequest("skip and limit must be integers")

        print(skip, limit, type(skip), type(limit))

        if skip < 0 or limit < 0 or limit > 5:
            return HttpResponseBadRequest(
                "skip and limit must be greater than 0 "
                "and limit must be leser than 40"
            )
        
        return function(
            request=request, skip=skip, limit=limit, *args, **kwargs)
    
    return wrapper