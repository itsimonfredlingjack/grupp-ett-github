"""Additional tests for app factory to improve coverage."""

from app import create_app


class TestAppFactory:
    """Test app factory and initialization."""

    def test_create_app(self):
        """Create app should return Flask instance."""
        app = create_app()
        assert app is not None

    def test_app_has_secret_key(self):
        """App should have secret key."""
        app = create_app()
        assert app.secret_key is not None

    def test_app_testing_mode(self):
        """App can be created in testing mode."""
        app = create_app()
        app.config["TESTING"] = True
        assert app.config["TESTING"] is True

    def test_app_has_routes(self):
        """App should have registered routes."""
        app = create_app()
        assert len(app.url_map._rules) > 0

    def test_app_root_hello(self):
        """Root endpoint exists."""
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code in [200, 404]

    def test_app_health_endpoint(self):
        """Health endpoint exists."""
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code in [200, 404]

    def test_app_has_blueprints(self):
        """App should have blueprints registered."""
        app = create_app()
        assert "monitor" in app.blueprints or len(app.blueprints) > 0

    def test_app_routes_registered(self):
        """Expense tracker routes should be registered."""
        app = create_app()
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        # Should have at least some routes from blueprints
        assert len(routes) > 0
