# TicketDesk - Test Plan

## 1. Scope
מה נבדק: [API, UI, DB של TicketDesk לפי המפרט בגרסה X]
מה לא נבדק: [performance, security scanning, accessibility, דפדפנים ניידים]

## 2. Test levels and tools
| Level | Tool | Why |
|---|---|---|
| API (integration) | pytest + requests | בדיקות מההירות וללא תלות בדפדפן |
| DB validation | sqlite3 |  לבדוק את הנכונות של המסדדי נתונים מאחורי הקלעים |
| UI (system) | pytest-playwright | ובכללי חוויית משתמשAPIכל מה שאא לבדוק ברמת ה |
| E2E | כל השלושה |בדיקות מקצה ללקצה מהממשק עד להחזרת התומאה דרך הדפדפן והשינוי במסד הנתונים|

## 3. Risks and priorities
| Risk | Impact | Coverage |
|---|---|---|
| reporter מצליח לבצע פעולה של agent/admin | high | טסטי 403 בכל endpoint מוגן |
| המעבר בן מצבי הטיקטים לא הגיוני וניתן לדלג על שלבים  |high | בדיקה של כל המעעברים הלא חוקיים כדי לבדוק שזה לא נותן|
|התחברות עם טוקן שהוא פג תוקף או טוקן לא חוקי שהצליח להתחבר|high|בדיקות שליליות עם טוקנים שפגו או לא תקינים |
## 4. Test cases
| ID | Area | Title | Level | Priority | Spec reference |
|---|---|---|---|---|---|
| TC-AUTH-001 | Auth | login with valid credentials returns token | API | smoke | POST /api/auth/login |
| TC-AUTH-002 | Auth | login with wrong password returns 401 | API | high | POST /api/auth/login |
| TC-TKT-003 | Tickets | create ticket with title of 3 chars (lower boundary) | API | high | validation rules |
| TC-TKT-004 | Auth|login with non-existent username returns 401 |API |high |POST /api/auth/login |
|  TC-TKT-005 | Auth| access protected endpoint without token returns 401| high| API| | Security
|  TC-TKT-006 | Auth| access protected endpoint with malformed token returns 401| medium| API| Security| 
|  TC-TKT-007 | Auth| access protected endpoint with malformed token returns 401| medium| API|Security | 
|  TC-TKT-008 | Tickets|create ticket with title of 3 chars |API |Low | validation|
|  TC-TKT-009 | Tickets|create ticket with descreption of 10 chars |API |Low | validation|
|  TC-TKT-010 | Tickets|create ticket with description under 10 chars returns 422 |API |Low | validation|
|  TC-TKT-011 | Tickets|create ticket with title of 1 chars |API |Low | validation|
|  TC-TKT-012 | Tickets|create ticket with title of 80 chars |API |Low | validation|
|  TC-TKT-013 | Tickets|create ticket with descreption of 81 chars |API |Low | validation|
|  TC-TKT-014 | Tickets|create ticket with empty status returns 422 |API |Low | validation|
|  TC-TKT-015 | Tickets|create ticket with invalid priority string returns 422 |API |medium | validation|
|  TC-TKT-016 | Workflow|transition ticket status from open to in_progress (valid)|API |high | State Machine|
|  TC-TKT-017 | Workflow|transition ticket status from open to resolved (valid) |API |high | State Machine|
|  TC-TKT-018 | Workflow|transition ticket status from open to closed (valid) |API |high | State Machine|
|  TC-TKT-019 | Workflow|ctransition ticket status from in_progress to resolved (valid) |API |high | State Machine|
|  TC-TKT-020 | Workflow|ctransition ticket status from resolved to closed (valid) |API |high | State Machine|
|  TC-TKT-021 | Workflow|transition ticket status from closed to open (invalid) |API |medium | State Machine|
|  TC-TKT-022 | Workflow|transition ticket status from closed to in_progress (invalid) |API |medium | State Machine|
|  TC-TKT-023 | Workflow|transition ticket status from closed to resolved (invalid) |API |medium | State Machine|
|  TC-TKT-024 | Workflow|transition ticket status from resolved to open (invalid)|API |medium | State Machine|
|  TC-TKT-025 | Workflow|transition ticket status from resolved to in_progress (invalid) |API |medium | State Machine|
|  TC-TKT-026 | Workflow|transition ticket status from in_progress to open (invalid) |API |medium | State Machine|
|  TC-TKT-027 | Workflow|transition ticket status from in_progress to closed (invalid) |API |high | State Machine|
|  TC-TKT-028 |Permissions|reporter attempts to delete ticket returns 403 |API |high | rulse|
|  TC-TKT-029 |Permissions|reporter attempts to assign ticket returns 403 |API |high | rulse|
|  TC-TKT-030 |Permissions|agent deletes ticket returns 403 (admin only action) |API |high | rulse|
|  TC-TKT-031 |Permissions|admin accesses system user management succeeds |API |high | rulse|
|  TC-TKT-032 |Permissions|reporter accesses system user management returns 403 |API |high | rulse|
|  TC-TKT-033 |filter|filter tickets list by status query param |API |medium | GET /api/tickets?status=|
|  TC-TKT-034 |filter|search tickets list by keyword in title |API |medium | GET /api/tickets?search=|
|  TC-TKT-035 |filter|pagination limits results using limit and offset |API |medium | GET /api/tickets?limit=|
|  TC-TKT-036 |UI|login page renders successfully and accepts input |UI |smoke |UI Login view |
|  TC-TKT-037 |UI|dashboard displays ticket table and items correctly |UI |smoke |UI Dashboard |
|  TC-TKT-038 |UI|create ticket modal opens and validates on client side |UI |high | UI Ticket Modal|
|  TC-TKT-039 |UI|clicking ticket row navigates smoothly to detail view |UI |medium | UI Navigation|
|  TC-TKT-040 |UI|status badge changes color dynamically upon patch |UI |low | UI View|
|  TC-TKT-041 |DB|verify ticket creation directly inside SQLite database |DB |high | Databace|








| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |
| ... | | | | | |

## 5. Test data strategy
[seed של 25 tickets, reset בתחילת ריצה, כל טסט יוצר נתונים ייחודיים ומוחק בסיום]


## 6. Entry and exit criteria
Entry: [השרת עולה, /api/health מחזיר 200]
Exit: [כל טסטי smoke עוברים, אין failures לא מוסברים, באגים פתוחים מסומנים xfail עם קישור ל-bug report]

## 7. Environment