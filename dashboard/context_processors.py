def site(request):
    verified = True
    if request.user.is_authenticated:
        prof = getattr(request.user, 'profile', None)
        verified = bool(prof and prof.email_verified)
    return {'SITE_NAME': 'CHEMVERSE', 'EMAIL_VERIFIED': verified}
