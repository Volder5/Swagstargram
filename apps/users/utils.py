from django.contrib import messages

"""def verify_session_code(request, session_key='registration_data'):
    input_code = request.POST.get('code')
    data = request.session.get(session_key, {})

    if input_code == data.get('code'):
        return True, data
    else:
        messages.error(request, "Invalid verification code")
        return False, {}"""