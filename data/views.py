from rest_framework.views import APIView
from .models import Games , About , GameInfo , Subscriber , ChatMessage , GuestUser
from rest_framework import status
from .serializers import (GameSerializer , GameInfoSerializer , AboutSerializer , ChatResponseSerializer
, ChatRequestSerializer , ChatHistorySerializer)
from .filters import GameFilter , AboutFilter
from rest_framework.response import Response
from rest_framework.filters import SearchFilter , OrderingFilter
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
import google.generativeai as genai
from django.conf import settings
from .utils import can_use_ai , get_client_ip
from datetime import date

class GameView(APIView):
    search_fields = ["game_name","release_date", "series" , "developer" , "publisher"]
    ordering_fields = ["release_date"]

    def get_object(self, pk=None):
        try:
            return Games.objects.get(pk=pk)
        except Games.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            obj = self.get_object(pk=pk)
            if not obj:
                return Response(
                    {"success": False, "message": "No record found with this ID"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = GameSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        queryset = Games.objects.all()
        filterset = GameFilter(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request,queryset,self)

        ordering_filter = OrderingFilter()
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            GameSerializer(queryset, many=True).data, status=status.HTTP_200_OK
        )

    def post(self,request,pk=None):
        if pk is not None:
            return Response({"error":"POST Cannot Work With Primary Key"},status=status.HTTP_400_BAD_REQUEST)
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request,pk=None):
        if pk is None:
            return Response(
                {"error": "PATCH requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj = self.get_object(pk=pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,)
        serializer = GameSerializer(obj,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data Patched successfully"},status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,pk=None):
        if pk is None:
            return Response({"error":"PUT requires the Primary Key"},
                            status=status.HTTP_401_UNAUTHORIZED
            )

        obj = self.get_object(pk=pk)
        if not obj:
            return Response({"error":"Object Data Not Found"},
                            status=status.HTTP_404_NOT_FOUND
            )
        serializer = GameInfoSerializer(obj,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class AboutView(APIView):
    search_fields = ["summary", "steam_appid", "game__game_name"]
    ordering_fields = ["id"]

    def get_object(self, pk=None):
        try:
            return About.objects.get(pk=pk)
        except About.DoesNotExist:
            return None

    # ---------------- GET ----------------
    def get(self, request, pk=None):
        if pk:
            obj = self.get_object(pk)
            if not obj:
                return Response(
                    {"success": False, "message": "No record found with this ID"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = AboutSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

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

        return Response(
            AboutSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )

    # ---------------- POST ----------------
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

    # ---------------- PATCH ----------------
    def patch(self, request, pk=None):
        if pk is None:
            return Response(
                {"error": "PATCH requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AboutSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Data patched successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- PUT ----------------
    def put(self, request, pk=None):
        if pk is None:
            return Response(
                {"error": "PUT requires a primary key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"error": "Object data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AboutSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Class ChatAPiView
class ChatAPIView(APIView):
    """
    Anonymous Chat API with:
    - Daily limit 4 messages
    - IP + Fingerprint tracking
    - Ban system
    """
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
            return Response({"error": "You are banned"}, status=status.HTTP_403_FORBIDDEN)

        if not can_use_ai(user):
            return Response({"error": "Daily limit reached (4 messages)"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Save user message
        ChatMessage.objects.create(user=user, role="user", message=message)
        user.daily_count += 1
        user.last_used = date.today()
        user.save()

        # Call Gemini AI
        genai.configure(api_key=settings.GENAI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"max_output_tokens": 2048, "temperature": 0.7}
        )
        try:
            response = model.generate_content(message)
            ai_response = response.text
        except Exception:
            ai_response = "AI service temporarily unavailable"

        # Save AI message
        ChatMessage.objects.create(user=user, role="ai", message=ai_response)

        response_data = ChatResponseSerializer({
            "response": ai_response,
            "remaining": 4 - user.daily_count
        }).data

        return Response(response_data, status=status.HTTP_200_OK)

class ChatHistoryAPIView(APIView):
    def get(self, request):
        guest_id = request.headers.get("X-GUEST-ID")
        user = GuestUser.objects.filter(uuid=guest_id).first()

        if not user:
            return Response({"messages": []}, status=200)

        messages = ChatMessage.objects.filter(user=user).order_by("created_at")

        serializer = ChatHistorySerializer(messages, many=True)
        return Response({"messages": serializer.data}, status=200)

def games_list_view(request):
    games = Games.objects.all()
    return render(request, "data/home.html", {"games": games})

def about_list_view(request):
    abouts = About.objects.all()
    return render(request, "data/about_list.html", {"abouts": abouts})

def gameinfo_list_view(request):
    infos = GameInfo.objects.all()
    return render(request, "data/gameinfo_list.html", {"infos": infos})

def game_detail_view(request, pk, slug):
    about = get_object_or_404(About, pk=pk)

    if about.game.slug != slug:
        return redirect(
            "game_detail",
            pk=about.pk,
            slug=about.game.slug
        )

    return render(request, "data/game_detail.html", {
        "about": about
    })

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


def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                send_mail(
                    subject="Subscription Confirmed",
                    message="Thank you for subscribing to CyberCarnage newsletter!",
                    from_email="yourorg@example.com",
                    recipient_list=[email],
                    fail_silently=False,
                )
                return JsonResponse({"status": "success"})
            return JsonResponse({"status": "exists"})
    return JsonResponse({"status": "error"})

def gemini_chat_view(request):
    return render(request, 'data/gemini_chat.html')
