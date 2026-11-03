## BUG-002 (suspected): search ignores description
- Spec: GET /api/tickets?q= searches title OR description
- Actual: only title is searched
- Repro: create ticket with unique word in description, GET /api/tickets?q=<word> -> items []
- Found by: tests/api/test_tickets_crud.py::test_search_matches_description

## BUG-003 (suspected): title length validation exceeds maximum limit
- Spec: Ticket title must not exceed 81 characters
- Actual: System successfully creates a ticket with a title longer than 81 characters (no validation error returned)
- Repro: Create a ticket with a title string containing 82+ characters -> POST /api/tickets -> returns 200/201 Created instead of 422 Unprocessable Entity
- Found by: tests/api/test_tickets_crud.py::test_create_ticket_title_max_length

## BUG-004 (suspected): priority sorting follows alphabetical order instead of logical severity
- Spec: Ticket priority sorting should follow logical severity order (Critical -> High -> Medium -> Low)
- Actual: System sorts priorities alphabetically (critical, high, low, medium)
- Repro: Create tickets with different priorities, call GET /api/tickets?sort=priority -> observe incorrect sorting sequence
- Found by: tests/api/test_tickets_crud.py::test_tickets_sorting_by_priority