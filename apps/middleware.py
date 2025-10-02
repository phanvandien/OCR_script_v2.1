import logging

logger = logging.getLogger(__name__)

class DebugMiddleware:
   def __init__(self, get_response):
      self.get_response = get_response

   def __call__(self, request):
       if request.path == '/upload/' and request.method =="POST":
           logger.info(f"Upload request received:")
           logger.info(f"FILES: {list(request.FILES.keys())}")
           logger.info(f"POST data: {dict(request.POST)}")
           if 'zip_file' in request.FILES:
              file_obj = request.FILES['zip_file']
              logger.info(f" File name: {file_obj.name}")
              logger.info(f" File size: {file_obj.size}")
              logger.info(f" Content type: {file_obj.content_type}")

       response = self.get_response(request)
       return response           

