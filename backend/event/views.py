from uuid import UUID

from django.db import transaction
from django.db.models import F
from rest_framework import exceptions, status
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core import constant
from event import models, serializers


def get_event(event_id, **filters) -> models.Event:
    try:
        UUID(str(event_id))
    except ValueError:
        raise exceptions.NotFound() from None
    return get_object_or_404(models.Event.objects.select_related('user'), id=event_id, **filters)


class CreateEventView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CreateEventSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GetUserEventsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.OwnerEventSerializer

    def get_queryset(self):
        return models.Event.objects.filter(active=True, user=self.request.user).order_by('-created_at')


class GetEventsView(ListAPIView):
    serializer_class = serializers.EventSerializer

    def get_queryset(self):
        return models.Event.objects.filter(active=True).select_related('user').order_by('start_date')


class GetEventView(APIView):
    """One event. Every request counts as a view."""

    def get(self, request: Request):
        event = get_event(request.query_params.get('id'), active=True)
        models.Event.objects.filter(pk=event.pk).update(watched=F('watched') + 1)
        event.refresh_from_db(fields=['watched'])
        return Response(serializers.EventSerializer(event, context={'request': request}).data)


class LoadImageView(CreateAPIView):
    """Image upload for Editor.js; answers in the format the image tool expects."""

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializers.ImageSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': 0, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response({'success': 1, 'file': {'url': serializer.data['image']}}, status=status.HTTP_201_CREATED)


class DeleteEventView(APIView):
    """Hide an event of the current user. It stays in the database."""

    permission_classes = (IsAuthenticated,)

    def delete(self, request: Request, id):
        event = get_event(id, user=request.user, active=True)
        event.active = False
        event.save(update_fields=['active'])
        return Response({'id': str(event.id)})


class LikeEventView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request: Request, id):
        with transaction.atomic():
            event = get_event(id, active=True)
            username = request.user.username
            if event.user_id == username or username in event.liked:
                raise exceptions.PermissionDenied('You cannot like this event.')
            event.liked.append(username)
            event.save(update_fields=['liked'])
        return Response({'liked': event.liked, 'likes': len(event.liked)})


class RegisterEventView(APIView):
    """Sign up for an event: name, email and contacts. No account is needed."""

    def patch(self, request: Request, id):
        with transaction.atomic():
            event = get_event(id, active=True)
            serializer = serializers.RegisterEventSerializer(data=request.data, context={'event': event})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class GetSpecialInfoView(APIView):
    def get(self, request: Request, key):
        lists = {'cities': constant.CITIES, 'tags': constant.TAGS}
        if key not in lists:
            raise exceptions.NotFound()
        return Response(lists[key])
