## BUG-001 (suspected): invalid transition from closed to open returns 200 instead of 409
- Spec: Closed is a terminal state; transitioning from closed to open is invalid and must return 409 Conflict
- Actual: System accepts the transition and returns 200 OK
- Repro: Create ticket -> move through workflow to closed -> call PATCH /api/tickets/{id} with status="open" -> returns 200 OK instead of 409
- Found by: tests/api/test_workflow.py::test_invalid_transition_returns_409[closed->open]

## BUG-002 (suspected): search ignores description
- Spec: GET /api/tickets?q= searches title OR description
- Actual: only title is searched
- Repro: create ticket with unique word in description, GET /api/tickets?q=<word> -> items []
- Found by: tests/api/test_tickets_crud.py::test_search_matches_description

## BUG-003 (suspected): title length validation exceeds maximum limit
- Spec: Ticket title must be between 3 and 80 characters; 81 characters must return 422
- Actual: System successfully creates a ticket with a title longer than 81 characters (no validation error returned)
- Repro: Create a ticket with a title string containing 82+ characters -> POST /api/tickets -> returns 200/201 Created instead of 422 Unprocessable Entity
- Found by: tests/api/test_tickets_crud.py::test_create_ticket_title_max_length