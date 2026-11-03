## BUG-002 (suspected): search ignores description
- Spec: GET /api/tickets?q= searches title OR description
- Actual: only title is searched
- Repro: create ticket with unique word in description, GET /api/tickets?q=<word> -> items []
- Found by: tests/api/test_tickets_crud.py::test_search_matches_description

