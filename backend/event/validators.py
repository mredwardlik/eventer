from rest_framework.exceptions import ValidationError

from core import constant


def validate_tags(tags):
    if not isinstance(tags, list) or not tags:
        raise ValidationError('Choose at least one tag.')
    wrong = [str(tag) for tag in tags if tag not in constant.TAGS]
    if wrong:
        raise ValidationError(f'Unknown tags: {", ".join(wrong)}.')
    if len(set(tags)) != len(tags):
        raise ValidationError('A tag is repeated.')
    return tags


def validate_city(city):
    if city not in constant.CITIES:
        raise ValidationError(f'Unknown city: {city}.')
    return city


def validate_description(description):
    if not isinstance(description, dict) or not isinstance(description.get('blocks', []), list):
        raise ValidationError('Expected an Editor.js document: {"blocks": [...]}.')
    return description
