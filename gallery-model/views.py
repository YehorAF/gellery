import functools
import hashlib
import secrets
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.utils import IntegrityError
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest, HttpResponseNotFound,\
    JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from gallery.forms import PictrueLoadingForm, SigninForm, AuthForm
from gallery.models import User, Picture, Follower, Reaction
from gallery.utils import check_auth, check_query_set_for_getting_data
from gallery.recognizer import nlp, recognizer


# picture functions


@require_http_methods(["GET"])
@check_query_set_for_getting_data
def get_pictures(request: HttpRequest, skip: int, limit: int):
    query = request.GET.get("q") or ""

    if query:
        doc = nlp(query)
        lemmas = [tok.lemma_ for tok in doc]
        filtered_sentence = []

        for word in lemmas:
            lex = nlp.vocab[word]
            if not lex.is_punct and not lex.is_stop:
                filtered_sentence.append(word)

        pictures = Picture.objects.filter(
            functools.reduce(
                Q.__and__, [Q(tags__icontains=word) for word in lemmas]
            )
        )
    else:
        pictures = Picture.objects.all()

    nskip = skip + limit if pictures.count() > skip + limit else None
    bskip = skip - limit if skip >= limit else None
    pictures = pictures[skip:skip+limit]
    pictures_answer = []

    for picture in pictures:
        reactions = Reaction.objects.filter(picture=picture.id).count()
        user = User.objects.get(id=picture.user.id)
        pictures_answer.append(
            picture.__dict__ | {
                "reactions": reactions, "username": user.username
        })

    return render(
        request, 
        "main.html", 
        {
            "pictures": pictures_answer, 
            "limit": limit, 
            "nskip": nskip,
            "bskip": bskip, 
            "q": query
        }
    )


@require_http_methods(["GET"])
def get_picture(request: HttpRequest, username: str, picture_id: int):
    try:
        user = User.objects.get(username=username)
        picture = Picture.objects.get(user=user.id, id=picture_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound(
            "not such user or picture"
        )

    reactions_cur = Reaction.objects.filter(picture=picture_id)
    reactions = reactions_cur.count()
    # is_reacted = reactions_cur.filter()

    return render(request, "picture.html", {
        "user": user,
        "picture": picture,
        "reactions": reactions
    })


@require_http_methods(["POST", "DELETE"])
@csrf_protect
@check_auth
def react(
    request: HttpRequest, 
    username: str, 
    user_id: int, 
    name: str, 
    picture_id: int
):
    try:
        user = User.objects.get(id=user_id)
        picture = Picture.objects.get(id=picture_id)
        react_cur = Reaction.objects.filter(user=user.id, picture=picture_id)

        if request.method == "POST" and not react_cur.exists():
            Reaction(picture=picture, user=user).save()
        else:
            react_cur.delete()

        reactions = Reaction.objects.filter(picture=picture_id).count()
    except ObjectDoesNotExist:
        return HttpResponseNotFound(
            "not such user or picture"
        )
    except IntegrityError:
        return HttpResponseBadRequest(
            "something go wrong"
        )

    return JsonResponse({"reactions": reactions})


# user functions


@require_http_methods(["GET"])
@check_auth
@check_query_set_for_getting_data
def get_users(
    request: HttpRequest, 
    user_id: int, 
    name: str, 
    skip: int, 
    limit: int
):    
    users = list(User.objects.all()[skip:skip+limit])
    users_answer = []

    for user in users:
        pictures = Picture.objects.filter(user=user.id).count()
        followed = Follower.objects.filter(
            influencer=user.id, follower=user_id).exists()
        users_answer.append(
            user.__dict__ | {"followed": followed, "pictures": pictures})

    return render(request, "users.html", {"users": users_answer})


@require_http_methods(["GET"])
@check_auth
@check_query_set_for_getting_data
def get_user(
    request: HttpRequest, 
    username: str, 
    user_id: int, 
    name: str, 
    skip: int, 
    limit: int
):
    try:
        if username == "me":
            query = {"id": user_id}
        else:
            query = {"username": username}

        user = User.objects.get(**query)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("there is not such user")
    
    followers = Follower.objects.filter(influencer=user.id).count()
    influencers = Follower.objects.filter(follower=user.id).count()
    followed = Follower.objects.filter(
        influencer=user.id, follower=user_id).exists()
    pictures = list(Picture.objects.filter(user=user.id)[skip:skip+limit])
    pictures_answer = []

    for picture in pictures:
        reactions = Reaction.objects.filter(picture=picture.id).count()
        pictures_answer.append(
            picture.__dict__ | 
            {"reactions": reactions, "username": user.username}
        )

    return render(
        request, 
        "user.html", 
        {
            "user": user, 
            "followed": followed, 
            "followers": followers, 
            "influencers": influencers,
            "pictures": pictures_answer,
            "amount_pictures": len(pictures)
        }
    )


@require_http_methods(["POST", "DELETE"])
@csrf_protect
@check_auth
def follow(request: HttpRequest, name: str, user_id: int, username: str):
    try:
        influencer = User.objects.get(username=username)
        follower = User.objects.get(id=user_id)
        follower_cur = Follower.objects.filter(
            influencer=influencer.id, follower=user_id)

        if request.method == "POST" and not follower_cur.exists():
            Follower(influencer=influencer, follower=follower).save()
        else:
            follower_cur.delete()

        followers = Follower.objects.filter(influencer=influencer.id).count()
    except ObjectDoesNotExist:
        return HttpResponseNotFound("there is not such follower")
    except IntegrityError:
        return HttpResponseBadRequest("something go wrong")
    
    return JsonResponse({"followers": followers})


# funcs with login action


@require_http_methods(["GET"])
def get_login_page(request: HttpRequest):
    return render(request, "login.html")


@require_http_methods(["POST"])
@csrf_protect
def signin(request: HttpRequest):
    form = SigninForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest("form is invalid")

    password = form.cleaned_data["password"]
    email = form.cleaned_data["email"]
    username = form.cleaned_data["username"]
    fullname = form.cleaned_data["fullname"]

    try:
        session = secrets.token_urlsafe(16)
        salt = secrets.token_urlsafe(8)
        password = hashlib.sha256(
            f"{salt}@{password}".encode()).hexdigest()
        user = User(
            email=email,
            username=username,
            fullname=fullname,
            password=password,
            salt=salt,
            session=session,
            status="user"
        )
        user.save()
    except IntegrityError:
        return HttpResponseBadRequest(
            "user with such email or username exists. try another")
    
    response = redirect("/")
    response.set_cookie("session", session)

    return response


@require_http_methods(["POST"])
@csrf_protect
def auth(request: HttpRequest):
    form = AuthForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest("form is not valid")
    
    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]

    try:
        user = User.objects.get(username=username)
        password = hashlib.sha256(
            f"{user.salt}@{password}".encode()).hexdigest()
        
        if password != user.password:
            raise ValueError("incorrect password")
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("not such user")
    except ValueError as ex_:
        return HttpResponseBadRequest(ex_)
    
    session = user.session
    
    response = redirect("/")
    response.set_cookie("session", session)

    return response


@require_http_methods(["GET", "POST"])
@check_auth
@csrf_protect
def logout(request: HttpRequest, user_id: int, name: str):
    session = secrets.token_urlsafe(16)

    user = User.objects.get(id=user_id)
    user.session = session
    user.save()

    return redirect("/login")


# uploading picture functions


@require_http_methods(["GET"])
@check_auth
def get_load_page(request: HttpRequest, user_id: int, name: str):
    return render(request, "load.html")


@require_http_methods(["POST"])
@check_auth
@csrf_protect
def upload_picture(request: HttpRequest, user_id: int, name: str):
    form = PictrueLoadingForm(request.POST, request.FILES)

    if not form.is_valid():
        return HttpResponseBadRequest("bad file")
    
    description = form.cleaned_data["description"]
    tags = (form.cleaned_data["tags"] or "").split(",")
    base_dir = os.path.join(settings.BASE_DIR, "user-files")

    if not os.path.exists(f"{base_dir}/{user_id}"):
        os.mkdir(f"{base_dir}/{user_id}")

    uid = secrets.token_urlsafe(16)
    fmt = request.FILES["picture"].name.split(".")[-1]
    link = f"user-files/{user_id}/{uid}.{fmt}"

    with open(link, "wb+") as fp:
        for chunk in request.FILES["picture"].chunks():
            fp.write(chunk)

    path = recognizer.convert_image_to_png(link, f"{link}.new")
    image = recognizer.load_image(path)
    _, results = recognizer.detect_objects(image)
    tags += recognizer.idx_to_words(results, 0.4)
    tags = set(tags)
    tags = ",".join(tags)

    user = User.objects.get(id=user_id)
    picture = Picture(
        user=user, link=link, description=description, tags=tags)
    picture.save()

    return redirect(f"/users/{name}")


@require_http_methods(["GET"])
def load_picture(request: HttpRequest, username: int, picture_id: int):
    try:
        user = User.objects.get(username=username)
        picture = Picture.objects.get(user=user.id, id=picture_id)
        link = picture.link

        with open(link, "rb") as fp:
            data = fp.read()
    except ObjectDoesNotExist:
        return HttpResponseNotFound("not such picture")
    except FileNotFoundError:
        return HttpResponseNotFound("not such picture")
    
    return HttpResponse(data)