from rest_framework.views import APIView
from .models import Games , About , GameInfo , Subscriber
from rest_framework import status
from .serializers import GameSerializer , GameInfoSerializer , AboutSerializer
from .filters import GameFilter , AboutFilter
from rest_framework.response import Response
from rest_framework.filters import SearchFilter , OrderingFilter
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt


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


def games_list_view(request):
    games = Games.objects.all()
    return render(request, "data/home.html", {"games": games})

def about_list_view(request):
    abouts = About.objects.all()
    return render(request, "data/about_list.html", {"abouts": abouts})

def gameinfo_list_view(request):
    infos = GameInfo.objects.all()
    return render(request, "data/gameinfo_list.html", {"infos": infos})

def about_detail_view(request, pk):
    about = get_object_or_404(About, pk=pk)
    return render(request, "data/about_detail.html", {"about": about})

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


@csrf_exempt
def gemini_chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('message', '')

        genai.configure(api_key="AIzaSyAl_y5Op44UWa8z9RvC0OALixHRTRPsaKA")

        model = genai.GenerativeModel(
            model_name="gemini-2.5-pro",
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.7,
            }
        )

        try:
            response = model.generate_content(user_input)
            ai_response = response.text
        except Exception as e:
            print("GEMINI ERROR:", e)
            ai_response = f"Error: {str(e)}"

        return JsonResponse({'response': ai_response})

    # GET request → render template
    return render(request, 'data/gemini_chat.html')