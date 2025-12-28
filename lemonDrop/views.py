from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

@csrf_exempt
def cron_job_view(request):
    secret_key = os.getenv("CRON_SECRET", "default-insecure-secret")
    request_secret = request.GET.get("secret") or request.headers.get("Authorization")

    if request_secret != secret_key:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        call_command("cleanup_messages")
        call_command("cleanup_tokens")
        return JsonResponse({"status": "success", "message": "Cleanup tasks executed."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
