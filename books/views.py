from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
from epub.core.http.renderer import JSRenderer


class JSView(APIView):
    renderer_classes = [JSRenderer]

    def get(self, request):
        return Response('var js=1;', content_type='application/javascript')

