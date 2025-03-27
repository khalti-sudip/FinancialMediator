from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security-related HTTP headers."""
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Strict-Transport-Security
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Permitted-Cross-Domain-Policies
        response['X-Permitted-Cross-Domain-Policies'] = 'none'
        
        # Referrer-Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature-Policy
        response['Feature-Policy'] = "geolocation 'none'; microphone 'none'; camera 'none'"
        
        return response
