from rest_framework.views import APIView
from .models import Games, About, GameInfo, Subscriber, ChatMessage, GuestUser
from rest_framework import status
from .serializers import (
    GameSerializer,
    GameInfoSerializer,
    AboutSerializer,
    ChatResponseSerializer,
    ChatRequestSerializer,
    ChatHistorySerializer,
)
from .filters import GameFilter, AboutFilter, InfoFilter
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from .utils import can_use_ai, get_client_ip , get_obj_or_404
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
import requests

class GameView(APIView):
    search_fields = ["game_name", "release_date", "series", "developer", "publisher"]
    ordering_fields = ["release_date"]

    def get(self, request, pk=None):
        if pk:
            obj, error = get_obj_or_404(Games, pk)
            if error:
                return error
            serializer = GameSerializer(obj)
            return Response(serializer.data)

        queryset = Games.objects.all()
        filterset = GameFilter(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request, queryset, self)

        ordering_filter = OrderingFilter()
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = GameSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk=None):
        if pk is not None:
            return Response(
                {"error": "POST Cannot Work With Primary Key"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        obj, error = get_obj_or_404(Games, pk)
        if error:
            return error
        serializer = GameSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data patched successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        obj, error = get_obj_or_404(Games, pk)
        if error:
            return error
        serializer = GameInfoSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AboutView(APIView):
    search_fields = ["summary", "steam_appid", "game__game_name"]
    ordering_fields = ["id"]

    def get(self, request, pk=None):
        if pk:
            obj, error = get_obj_or_404(About, pk)
            if error:
                return error
            serializer = AboutSerializer(obj)
            return Response(serializer.data)

        queryset = About.objects.all()
        filterset = AboutFilter(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request, queryset, self)

        ordering_filter = OrderingFilter()
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 4
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = AboutSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk=None):
        if pk is not None:
            return Response(
                {"error": "POST cannot work with primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AboutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request,pk=None):
        obj, error = get_obj_or_404(About, pk)
        if error:
            return error
        serializer = AboutSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        obj, error = get_obj_or_404(About, pk)
        if error:
            return error
        serializer = AboutSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GameInfo Views

class GameInfoView(APIView):
    search_fields = ["game", "composer"]
    ordering_fields = ["multiplayer", "playable"]

    def get__object(self, pk=None):
        try:
            return GameInfo.objects.get(pk=pk)
        except GameInfo.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            obj, error = get_obj_or_404(GameInfo, pk)
            if error:
                return error
            serializer = GameInfoSerializer(obj)
            return Response(serializer.data)

        queryset = GameInfo.objects.all()
        filterset = InfoFilter(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request, queryset, self)

        order_filter = OrderingFilter()
        queryset = order_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 4
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = GameInfoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk=None):
        if pk is not None:
            return Response(
                {"error": "POST cannot use while Primary Key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = GameInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        obj, error = get_obj_or_404(About, pk)
        if error:
            return error
        serializer = GameInfoSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        obj, error = get_obj_or_404(GameInfo, pk)
        if error:
            return error
        serializer = GameInfoSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data updated successfully"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def can_use_ai(user):
    today = date.today()
    if user.last_used != today:
        user.daily_count = 0
    return user.daily_count < 4


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = serializer.validated_data["message"]
        guest_id = request.headers.get("X-GUEST-ID")
        fingerprint = request.headers.get("X-FINGERPRINT")
        ip_address = get_client_ip(request)

        if not guest_id:
            return Response({"error": "Guest ID missing"}, status=400)

        user, created = GuestUser.objects.get_or_create(uuid=guest_id)
        if created:
            user.ip_address = ip_address
            user.fingerprint = fingerprint
            user.save()

        if user.is_banned:
            return Response(
                {"error": "You are banned"}, status=status.HTTP_403_FORBIDDEN
            )

        if not can_use_ai(user):
            return Response(
                {"error": "Daily limit reached (4 messages)"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        ChatMessage.objects.create(user=user, role="user", message=message)
        today = date.today()
        if user.last_used != today:
            user.daily_count = 0
        user.daily_count += 1
        user.last_used = today
        user.save()

        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GENAI_API_KEY)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={"max_output_tokens": 2048, "temperature": 0.7},
            )
            response = model.generate_content(message)
            ai_response = response.text
        except Exception as e:
            ai_response = f"AI Error: {str(e)}"

        ChatMessage.objects.create(user=user, role="ai", message=ai_response)

        response_data = ChatResponseSerializer(
            {"response": ai_response, "remaining": 4 - user.daily_count}
        ).data

        return Response(response_data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class ChatHistoryAPIView(APIView):
    def get(self, request):
        guest_id = request.headers.get("X-GUEST-ID")
        if not guest_id:
            return Response({"messages": []}, status=200)

        user = GuestUser.objects.filter(uuid=guest_id).first()
        if not user:
            return Response({"messages": []}, status=200)

        messages = ChatMessage.objects.filter(user=user).order_by("created_at")
        serializer = ChatHistorySerializer({"messages": messages})
        return Response(serializer.data, status=200)


# def games_list_view(request):
#     all_games_qs = Games.objects.all().prefetch_related("details").order_by("-created_at")
#     games = all_games_qs
#
#     name = request.GET.get("name")
#     series_filter = request.GET.get("series")
#     company_filter = request.GET.get("developer")
#     platform_filter = request.GET.get("platform")
#     year_filter = request.GET.get("year")
#     steam_appid_filter = request.GET.get("steam")
#
#     if name:
#         games = games.filter(game_name__icontains=name)
#     if series_filter:
#         games = games.filter(series__icontains=series_filter)
#     if company_filter:
#         games = games.filter(developer__icontains=company_filter)
#     if platform_filter:
#         games = games.filter(details__platform__icontains=platform_filter)
#     if year_filter:
#         games = games.filter(release_date__year=year_filter)
#     if steam_appid_filter:
#         games = games.filter(details__steam_appid__icontains=steam_appid_filter)
#
#     games = games.distinct()
#
#     paginator = Paginator(games, 8)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)
#
#     series_list = all_games_qs.exclude(series__isnull=True).values_list("series", flat=True).distinct().order_by("series")
#     developer_list = all_games_qs.exclude(developer__isnull=True).values_list("developer", flat=True).distinct().order_by("developer")
#
#     platform_set = set()
#     for game in all_games_qs.prefetch_related("details"):
#         detail = game.details.first()
#         if detail and detail.platform:
#             platform_set.add(detail.platform)
#     platform_list = sorted(platform_set)
#
#     year_set = set()
#     for game in all_games_qs.exclude(release_date__isnull=True):
#         year_set.add(game.release_date.year)
#     year_list = sorted(year_set, reverse=True)
#
#     context = {
#         "page_obj": page_obj,
#         "all_games": all_games_qs,
#         "series_list": series_list,
#         "developer_list": developer_list,
#         "platform_list": platform_list,
#         "year_list": year_list,
#     }
#     return render(request, "data/home.html", context)

def games_list_view(request):
    all_games_qs = Games.objects.all().prefetch_related("details").order_by("-created_at")
    games = all_games_qs

    name = request.GET.get("name")
    series_filter = request.GET.get("series")
    company_filter = request.GET.get("developer")
    platform_filter = request.GET.get("platform")
    year_filter = request.GET.get("year")
    steam_appid_filter = request.GET.get("steam")

    if name:
        games = games.filter(game_name__icontains=name)
    if series_filter:
        games = games.filter(series__icontains=series_filter)
    if company_filter:
        games = games.filter(developer__icontains=company_filter)
    if platform_filter:
        games = games.filter(details__platform__icontains=platform_filter)
    if year_filter:
        games = games.filter(release_date__year=year_filter)
    if steam_appid_filter:
        games = games.filter(details__steam_appid__icontains=steam_appid_filter)

    games = games.distinct()

    # --- Pagination ---
    paginator = Paginator(games, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --- Lists for filters ---
    series_list = all_games_qs.exclude(series__isnull=True).values_list("series", flat=True).distinct().order_by("series")
    developer_list = all_games_qs.exclude(developer__isnull=True).values_list("developer", flat=True).distinct().order_by("developer")

    platform_set = set()
    for game in all_games_qs.prefetch_related("details"):
        detail = game.details.first()
        if detail and detail.platform:
            platform_set.add(detail.platform)
    platform_list = sorted(platform_set)

    year_set = set()
    for game in all_games_qs.exclude(release_date__isnull=True):
        year_set.add(game.release_date.year)
    year_list = sorted(year_set, reverse=True)

    latest_game = all_games_qs[:1]  # latest 5 games, adjust as needed

    context = {
        "page_obj": page_obj,
        "all_games": all_games_qs,
        "series_list": series_list,
        "developer_list": developer_list,
        "platform_list": platform_list,
        "year_list": year_list,
        "latest_game": latest_game,
    }

    return render(request, "data/home.html", context)

def about_list_view(request):
    abouts = About.objects.all()
    return render(request, "data/about_list.html", {"abouts": abouts})

def in_game_info_list_view(request):
    infos = GameInfo.objects.all()
    return render(request, "data/in-game info.html", {"infos": infos})


def game_detail_view(request, pk, slug):
    about = get_object_or_404(About.objects.select_related("game"), pk=pk)

    if about.game.slug != slug:
        return redirect(
            "game_detail", pk=about.pk, slug=about.game.slug, permanent=True
        )

    return render(request, "data/game_detail.html", {"about": about})


def privacy_page(request):
    return render(request, "data/privacy.html")


def terms_page(request):
    return render(request, "data/terms.html")


def faq_page(request):
    return render(request, "data/faq.html")


def send_contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        final_message = f"""
        New Contact Message
        -------------------------
        Name: {name}
        Email: {email}
        Message:
        {message}
        """

        send_mail(
            subject=f"New Contact Message from {name}",
            message=final_message,
            from_email=email,
            recipient_list=["ai8526304@gmail.com"],
            fail_silently=False,
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"})

@csrf_exempt
def subscribe_newsletter(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    email = request.POST.get("email")
    if not email:
        return JsonResponse({"status": "error"}, status=400)

    subscriber, created = Subscriber.objects.get_or_create(email=email)

    if not created:
        return JsonResponse({"status": "exists"})

    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "CyberCarnage <newsletter@cybercarnage.online>",
                "to": [email],
                "subject": "Subscription Confirmed",
                "html": """
                    <h2>Welcome to CyberCarnage ⚡</h2>
                    <p>You are now subscribed to gaming updates.</p>
                    <p>If you don’t see future emails, check <b>Spam / Promotions</b>.</p>
                """,
            },
            timeout=10,
        )
    except Exception:
        pass

    return JsonResponse({"status": "success"})

def gemini_chat_view(request):
    return render(request, "data/gemini_chat.html")