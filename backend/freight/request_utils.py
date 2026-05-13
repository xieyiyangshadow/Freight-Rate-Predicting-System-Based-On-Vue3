import json


def extract_user_id(request):
    header_value = request.headers.get('X-Client-User')
    if header_value:
        try:
            parsed = json.loads(header_value)
            if isinstance(parsed, dict) and parsed.get('id'):
                return int(parsed['id'])
        except Exception:
            try:
                return int(header_value)
            except Exception:
                pass

    if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
        return request.user.id

    try:
        if hasattr(request, 'data'):
            owner_value = request.data.get('owner')
            if owner_value:
                try:
                    return int(owner_value)
                except Exception:
                    pass
    except Exception:
        pass
    return None
