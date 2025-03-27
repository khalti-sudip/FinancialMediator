from django.utils.deprecation import MiddlewareMixin
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
import time

class OpenTelemetryMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)
        self.tracer = trace.get_tracer(__name__)

    def process_request(self, request):
        span = self.tracer.start_span(
            name=f"http.request.{request.method.lower()}".lower(),
            kind=SpanKind.SERVER,
            attributes={
                "http.method": request.method,
                "http.url": request.build_absolute_uri(),
                "http.scheme": request.scheme,
                "http.target": request.path,
                "http.host": request.get_host(),
                "http.user_agent": request.META.get("HTTP_USER_AGENT", "")[:256],
                "http.flavor": "1.1",
                "net.peer.ip": request.META.get("REMOTE_ADDR", ""),
                "net.peer.port": request.META.get("REMOTE_PORT", ""),
            }
        )
        trace.set_span_in_context(span)
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        span = trace.get_current_span()
        if span:
            span.set_status(Status(StatusCode.OK))
            span.set_attributes({
                "http.status_code": response.status_code,
                "http.status_text": response.reason_phrase,
                "http.response_content_length": len(response.content),
                "http.response_content_type": response.get("Content-Type", ""),
            })
            span.end()
        
        return response

    def process_exception(self, request, exception):
        span = trace.get_current_span()
        if span:
            span.set_status(Status(StatusCode.ERROR, str(exception)))
            span.record_exception(exception)
            span.end()
