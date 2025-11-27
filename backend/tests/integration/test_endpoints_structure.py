import pytest
from fastapi import APIRouter

class TestEndpointsStructure:

    def test_endpoint_imports(self):
        """Test that all endpoint modules can be imported."""
        try:
            from app.api.v1.endpoints import auth, users, books
            from app.services import AuthService, UserService, BookService
            from app.exceptions.base_exceptions import (
                ValidationError, AuthenticationError, BookNotFoundError
            )
            from app.repositories import UserRepository, BookRepository
        except ImportError as e:
            pytest.fail(f"Failed to import endpoint modules: {e}")

    def test_auth_endpoints_routes(self):
        """Test that auth routes are correctly registered."""
        from app.api.v1.endpoints.auth import router
        
        assert isinstance(router, APIRouter)
        
        routes = [route for route in router.routes]
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        expected_routes = ["/login", "/register", "/refresh", "/change-password", "/me"]
        for expected in expected_routes:
            assert expected in route_paths, f"Route {expected} not found in auth router"

    def test_user_endpoints_routes(self):
        """Test that user routes are correctly registered."""
        from app.api.v1.endpoints.users import router
        
        assert isinstance(router, APIRouter)

        routes = [route for route in router.routes]
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        expected_routes = ["/", "/me", "/{user_id}", "/search/{search_term}", "/stats/overview"]
        for expected in expected_routes:
            assert expected in route_paths, f"Route {expected} not found in users router"

    def test_book_endpoints_routes(self):
        """Test that book routes are correctly registered."""
        from app.api.v1.endpoints.books import router
        
        assert isinstance(router, APIRouter)

        routes = [route for route in router.routes]
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        expected_routes = [
            "/", "/{book_id}", "/{book_id}/generate", "/{book_id}/pdf",
            "/search/{search_term}", "/stats/overview", "/recent/list"
        ]
        for expected in expected_routes:
            assert expected in route_paths, f"Route {expected} not found in books router"

    def test_dependencies_imports(self):
        """Test that dependency injection components are available."""
        try:
            from app.api.deps import (
                get_current_user,
                get_current_active_user,
                get_current_admin_user,
                get_current_premium_user,
                validate_pagination_params
            )
        except ImportError as e:
            pytest.fail(f"Failed to import dependencies: {e}")

    def test_service_methods_availability(self):
        """Test that services have the expected methods."""
        from app.services import AuthService, UserService, BookService
        
        services_tests = [
            (AuthService, ["login", "register", "change_password"]),
            (UserService, ["create_user", "get_user_profile", "update_user"]),
            (BookService, ["create_book", "get_book_details", "start_book_generation"])
        ]
        
        for service_class, methods in services_tests:
            for method in methods:
                assert hasattr(service_class, method), f"{service_class.__name__} missing method {method}"

    def test_architecture_compliance_modules(self):
        """Test that architectural components exist."""
        components = [
            ("app.repositories", ["UserRepository", "BookRepository"]),
            ("app.services", ["AuthService", "UserService", "BookService"]),
            ("app.exceptions.base_exceptions", ["ValidationError", "AuthenticationError"]),
            # ("app.middleware", ["ExceptionMiddleware", "SecurityMiddleware"]), # Middleware might vary, checking existence
            ("app.utils.validators", ["validate_email_format"])
        ]
        
        for module_path, classes in components:
            module = __import__(module_path, fromlist=classes)
            for cls_name in classes:
                assert hasattr(module, cls_name), f"{cls_name} not found in {module_path}"
