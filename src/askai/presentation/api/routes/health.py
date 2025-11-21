"""
Health check and status endpoints for the AskAI API.
"""
from flask import current_app
from flask_restx import Namespace, Resource, fields

# Create namespace
health_ns = Namespace('health', description='Health check and status operations')

# Response models
health_response = health_ns.model('HealthResponse', {
    'status': fields.String(required=True, description='Service status', example='healthy'),
    'version': fields.String(required=True, description='API version', example='1.0.0'),
    'timestamp': fields.DateTime(required=True, description='Current timestamp'),
    'uptime': fields.Float(description='Service uptime in seconds'),
})

status_response = health_ns.model('StatusResponse', {
    'api': fields.String(required=True, description='API status', example='running'),
    'database': fields.String(description='Database status', example='connected'),
    'dependencies': fields.Raw(description='Dependency status'),
})


@health_ns.route('/health')
class Health(Resource):
    """Health check endpoint."""

    @health_ns.doc('health_check')
    @health_ns.marshal_with(health_response)
    def get(self):
        """Get service health status.

        Returns basic health information about the service.
        """
        import datetime  # pylint: disable=import-outside-toplevel
        import time  # pylint: disable=import-outside-toplevel

        # Get app start time (simplified for now)
        start_time = getattr(current_app, 'start_time', time.time())
        uptime = time.time() - start_time

        return {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.datetime.utcnow(),
            'uptime': uptime
        }


@health_ns.route('/status')
class Status(Resource):
    """Detailed status endpoint."""

    @health_ns.doc('service_status')
    @health_ns.marshal_with(status_response)
    def get(self):
        """Get detailed service status.

        Returns detailed status information including dependencies.
        """
        try:
            # Check core components (simplified for now)
            dependencies = {
                'patterns': 'available',
                'ai_service': 'available',
                'config': 'loaded'
            }

            return {
                'api': 'running',
                'database': 'not_applicable',
                'dependencies': dependencies
            }
        except Exception as e:
            current_app.logger.error(f"Status check failed: {e}")
            return {
                'api': 'degraded',
                'database': 'not_applicable',
                'dependencies': {'error': str(e)}
            }, 503


@health_ns.route('/ready')
class Readiness(Resource):
    """Readiness probe endpoint."""

    @health_ns.doc('readiness_check')
    def get(self):
        """Check if service is ready to serve requests.

        Returns 200 if ready, 503 if not ready.
        """
        try:
            # Perform readiness checks
            # For now, just return ready
            return {'ready': True}, 200
        except Exception as e:
            current_app.logger.error(f"Readiness check failed: {e}")
            return {'ready': False, 'error': str(e)}, 503


@health_ns.route('/live')
class Liveness(Resource):
    """Liveness probe endpoint."""

    @health_ns.doc('liveness_check')
    def get(self):
        """Check if service is alive.

        Returns 200 if alive, 503 if dead.
        """
        return {'alive': True}, 200
