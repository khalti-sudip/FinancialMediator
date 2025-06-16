from django.utils.deprecation import MiddlewareMixin

class SecurityMiddleware(MiddlewareMixin):
    """Middleware to add security-related HTTP headers."""
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'"
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Force HTTPS
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Control referrer information
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
