from rest_framework import serializers

class HealthStatusSerializer(serializers.Serializer):
    """Serializer for system health status."""
    
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database = serializers.DictField()
    redis = serializers.DictField()
    celery = serializers.DictField()
    
    def to_representation(self, instance):
        """Custom representation of health status."""
        return {
            'status': 'healthy' if all(
                instance['database']['status'] == 'healthy',
                instance['redis']['status'] == 'healthy',
                instance['celery']['status'] == 'healthy'
            ) else 'unhealthy',
            'timestamp': instance['timestamp'],
            'database': instance['database'],
            'redis': instance['redis'],
            'celery': instance['celery']
        }
