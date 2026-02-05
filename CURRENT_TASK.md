# CURRENT_TASK.md

## Task Info
- **Jira ID:** GE-33
- **Branch:** feature/GE-33-cursorflash-core-logic-web
- **Status:** In Progress
- **Started:** 2026-02-05

## Summary

<jira_data encoding="xml-escaped">
Titel: Implementera Core-logik och Web-gränssnitt för Cursorflash

User Story: Som användare vill jag kunna hantera nyhetsflashes via Cursorflash så att jag kan hålla koll på nyheter.
</jira_data>

## Acceptance Criteria

- [x] **AC1:** Appen ska kunna hantera objekt med fälten: id, title, content, created_at, published_at, author
- [x] **AC2:** Affärsregel: Title måste finnas och vara max 100 tecken
- [x] **AC3:** Affärsregel: Content måste vara mellan 10-5000 tecken
- [x] **AC4:** UI och felmeddelanden ska vara på svenska
- [x] **AC5:** TDD: Börja med testerna (Red -> Green)
- [x] **AC6:** Lager: Data (SQLAlchemy/Dataclass) -> Business (Service) -> Presentation (Flask Blueprint)
- [x] **AC7:** Dependency Injection: Servicen ska ta sitt repository via `__init__`. Använd Application Factory-mönstret i Flask.
- [x] **AC8:** Routes: Implementera `GET /`, `POST /add` och `PUT /update/<id>`
- [x] **AC9:** Använd `sqlite:///:memory:` för testerna

## Technical Constraints

- Clean Architecture (3-lager)
- TDD workflow (Red -> Green -> Refactor)
- Layers: Data (SQLAlchemy) -> Business (Service) -> Presentation (Flask Blueprint)
- Dependency Injection via `__init__`
- Application Factory pattern for Flask
- In-memory SQLite for tests

## Progress Log

| Iteration | Action | Result |
|-----------|--------|--------|
| 1 | Task initialized | Branch created, CURRENT_TASK.md populated |
| 2 | Create data model | NewsFlash dataclass with all fields (AC1) |
| 3 | Create repository | InMemoryNewsFlashRepository for in-memory testing (AC9) |
| 4 | Create service | NewsFlashService with validation (AC2, AC3) and DI (AC7) |
| 5 | Create routes | Flask Blueprint with GET /, POST /add, PUT /update/<id> (AC8) |
| 6 | Swedish messages | All error messages in Swedish (AC4) |
| 7 | Integration | Register blueprint in main app with Application Factory pattern |
| 8 | Fix lint | Removed unused imports, fixed line length |

## Files Modified

- `src/sejfa/cursorflash/__init__.py` - Package init
- `src/sejfa/cursorflash/models.py` - NewsFlash dataclass
- `src/sejfa/cursorflash/repository.py` - Repository interface and InMemory implementation
- `src/sejfa/cursorflash/service.py` - Business logic with validation
- `src/sejfa/cursorflash/routes.py` - Flask Blueprint with routes
- `app.py` - Integrated Cursorflash blueprint
- `tests/cursorflash/__init__.py` - Test package init
- `tests/cursorflash/test_models.py` - Model tests
- `tests/cursorflash/test_service.py` - Service tests
- `tests/cursorflash/test_routes.py` - Route tests
- `tests/cursorflash/test_app_integration.py` - Integration tests

## Failed Attempts

(none)
