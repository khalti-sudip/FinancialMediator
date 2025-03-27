Authentication
==============

FinancialMediator uses JWT-based authentication for secure API access.

Endpoints
---------

.. http:post:: /api/auth/login/

   Login endpoint for obtaining JWT tokens.

   **Example request**:

   .. sourcecode:: http

      POST /api/auth/login/ HTTP/1.1
      Content-Type: application/json

      {
          "username": "user",
          "password": "password"
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
          "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      }

.. http:post:: /api/auth/refresh/

   Refresh endpoint for obtaining new access tokens.

   **Example request**:

   .. sourcecode:: http

      POST /api/auth/refresh/ HTTP/1.1
      Content-Type: application/json

      {
          "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      }
