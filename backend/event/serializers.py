from datetime import datetime, timezone

from rest_framework import serializers

from event import models, validators


class TimestampField(serializers.DateTimeField):
    """Accepts Unix seconds as the frontend sends them, or an ISO date; returns ISO dates."""

    def to_internal_value(self, value):
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()):
            try:
                return datetime.fromtimestamp(float(value), tz=timezone.utc)
            except (OverflowError, OSError, ValueError):
                self.fail('invalid', format='Unix seconds')
        return super().to_internal_value(value)


class EventSerializer(serializers.ModelSerializer):
    """An event as everybody sees it. The list of registered guests is private."""

    user = serializers.CharField(source='user.username', read_only=True)
    likes = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = ('id', 'user', 'name', 'image', 'start_date', 'end_date', 'description', 'tags', 'city',
                  'created_at', 'watched', 'liked', 'likes')
        read_only_fields = fields

    def get_likes(self, event) -> int:
        return len(event.liked)


class CreateEventSerializer(serializers.ModelSerializer):
    start_date = TimestampField(required=False, allow_null=True)
    end_date = TimestampField(required=False, allow_null=True)
    tags = serializers.JSONField(validators=[validators.validate_tags])
    city = serializers.CharField(validators=[validators.validate_city])
    description = serializers.JSONField(required=False, validators=[validators.validate_description])

    class Meta:
        model = models.Event
        fields = ('id', 'name', 'image', 'start_date', 'end_date', 'description', 'tags', 'city')
        read_only_fields = ('id',)

    def validate(self, attrs):
        start, end = attrs.get('start_date'), attrs.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'The event cannot end before it starts.'})
        return attrs


class OwnerEventSerializer(serializers.ModelSerializer):
    """An event in the cabinet of its organizer, with the registered guests."""

    class Meta:
        model = models.Event
        fields = ('id', 'name', 'image', 'start_date', 'end_date', 'tags', 'city', 'created_at', 'watched',
                  'liked', 'registered', 'active')
        read_only_fields = fields


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = models.Image
        fields = ('image',)


class RegisterEventSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    contacts = serializers.CharField(max_length=200)

    def validate_email(self, email):
        event = self.context['event']
        if any(guest.get('email', '').lower() == email.lower() for guest in event.registered):
            raise serializers.ValidationError('This email is already registered for the event.')
        return email

    def save(self):
        event = self.context['event']
        event.registered.append(dict(self.validated_data))
        event.save(update_fields=['registered'])
        return event
