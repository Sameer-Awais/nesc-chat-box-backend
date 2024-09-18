from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # This logs in the user using Django's session framework
                # Send back user details
                return Response({
                    "message": "Login successful!",
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    }
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        logout(request)  # This logs out the user
        return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)

class GetUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def get(self, request):
    #     users = self.get_queryset()  # Fetch all users
    #     serializer = self.get_serializer(users, many=True)  # Serialize users
    #     return Response(serializer.data, status=status.HTTP_200_OK)
