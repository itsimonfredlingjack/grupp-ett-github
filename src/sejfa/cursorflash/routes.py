"""Flask Blueprint for Cursorflash routes (presentation layer)."""

from flask import Blueprint, jsonify, request

from src.sejfa.cursorflash.service import NewsFlashService, ValidationError


def create_cursorflash_blueprint(service: NewsFlashService) -> Blueprint:
    """Create Flask Blueprint with Cursorflash routes.

    Uses dependency injection - receives the service instance.

    Args:
        service: NewsFlashService instance.

    Returns:
        Blueprint: Configured Flask Blueprint.
    """
    bp = Blueprint("cursorflash", __name__)

    @bp.route("/", methods=["GET"])
    def list_flashes():
        """List all news flashes.

        Returns:
            Response: JSON with list of all flashes.
        """
        flashes = service.list_flashes()
        return jsonify(
            {
                "flashes": [
                    {
                        "id": f.id,
                        "title": f.title,
                        "content": f.content,
                        "created_at": f.created_at.isoformat(),
                        "author": f.author,
                        "published_at": f.published_at.isoformat()
                        if f.published_at
                        else None,
                    }
                    for f in flashes
                ]
            }
        ), 200

    @bp.route("/add", methods=["POST"])
    def add_flash():
        """Create a new news flash.

        Expects JSON with title, content, and author.

        Returns:
            Response: JSON with created flash or error message in Swedish.
        """
        data = request.get_json()

        if not data:
            return jsonify({"fel": "JSON-data krävs"}), 400

        title = data.get("title", "")
        content = data.get("content")
        author = data.get("author")

        if content is None:
            return jsonify({"fel": "Innehåll krävs"}), 400

        if author is None:
            return jsonify({"fel": "Författare krävs"}), 400

        try:
            flash = service.create_flash(
                title=title,
                content=content,
                author=author,
            )
            return jsonify(
                {
                    "id": flash.id,
                    "title": flash.title,
                    "content": flash.content,
                    "created_at": flash.created_at.isoformat(),
                    "author": flash.author,
                    "published_at": flash.published_at.isoformat()
                    if flash.published_at
                    else None,
                }
            ), 201
        except ValidationError as e:
            return jsonify({"fel": str(e)}), 400

    @bp.route("/update/<int:flash_id>", methods=["PUT"])
    def update_flash(flash_id: int):
        """Update an existing news flash.

        Args:
            flash_id: ID of the flash to update.

        Returns:
            Response: JSON with updated flash or error message in Swedish.
        """
        data = request.get_json()

        if not data:
            return jsonify({"fel": "JSON-data krävs"}), 400

        title = data.get("title")
        content = data.get("content")

        try:
            flash = service.update_flash(
                flash_id=flash_id,
                title=title,
                content=content,
            )

            if flash is None:
                return jsonify({"fel": "Nyhetsflash hittades inte"}), 404

            return jsonify(
                {
                    "id": flash.id,
                    "title": flash.title,
                    "content": flash.content,
                    "created_at": flash.created_at.isoformat(),
                    "author": flash.author,
                    "published_at": flash.published_at.isoformat()
                    if flash.published_at
                    else None,
                }
            ), 200
        except ValidationError as e:
            return jsonify({"fel": str(e)}), 400

    return bp
