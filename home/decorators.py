from django.shortcuts import redirect

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):

            # ✅ CORRECT attribute name (matches model)
            if not hasattr(request.user, 'userprofilexx'):
                return redirect('login')  # safer than unauthorized

            if request.user.userprofilexx.role != role:
                return redirect('login')

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
