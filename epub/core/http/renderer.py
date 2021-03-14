from rest_framework.renderers import BaseRenderer


class JSRenderer(BaseRenderer):
    media_type = 'application/javascript'
    format = 'javascript'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
