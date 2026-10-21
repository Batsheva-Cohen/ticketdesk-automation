               | פעולה ב-UI | בקשת HTTP שנשלחת |Status  | מה השתנה ב DB |
|-------------|------------------ | :----------------- | :------------------------- | :------------- |
| **login** |התחברות SIGNIN |"POST /login HTTP/1.1 |200 | נוצר טוקן של המשתמש בזיכרון של המחשב|
| **טעינת רשימה עם filter** |Status Open Priority Low|200 |"GET /api/tickets?status=open&priority=low&page=1&page_size=10 HTTP/1.1" | נשאר אותו דבר|
| **יצירת ticket** | new ticket |"POST /api/tickets HTTP/1.1" | 201 | נוספה שורה של משימה במצב קריטי|
| **שינוי סטטוס חוקי** |שינוי ממצב פתוח לבתהליך |PATCH /api/tickets/29 HTTP/1.1 | 200|אותה השורה רק השתנה ממצב פתוח למצב בתהליך |
| **שינוי סטטוס לא חוקי** | שינוי ממצב בתהליך למצב סגור| PATCH /api/tickets/29 HTTP/1.1| 409|לא השתנה כלום |
| **הוספת comment** |Add comments-hiiii | POST /api/tickets/29/comments HTTP/1.1"| 201| נןספה הערה לכרטיס 29 |
| **מחיקה כ-admin** | delete על משימה 27| DELETE /api/tickets/27 HTTP/1.1 | 204| משימה 27 כבר לא קיימת|
| **מחיקה כ-reporter** | אני לא יכולה למחוק כרפורט מכיוון שלא קיים בממשק אופצייץ מחיקה 

**קבלת טוקן חדש עבור מנהל**
curl.exe -X POST "http://127.0.0.1:8000/api/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"admin\", \"password\": \"Admin123!\"}"
**יצירת טיקט חדש עם הטוקן שקיבלתי**
curl.exe -X POST "http://127.0.0.1:8000/api/tickets" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MjYwNzkxMn0.jmAk5ZKck_Fj0b7tJG3Kt4pF7zMEUPvGTjKyjpglV8o" -H "Content-Type: application/json" -d "{\"title\": \"API Test Ticket\", \"description\": \"Detailed description of the bug for testing purposes.\", \"priority\": \"high\"}"
**שינוי הסטטוס של הטיקט 27 לבתהליך**
curl.exe -X PATCH "http://127.0.0.1:8000/api/tickets/27" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MjYwNzkxMn0.jmAk5ZKck_Fj0b7tJG3Kt4pF7zMEUPvGTjKyjpglV8o" -H "Content-Type: application/json" -d "{\"status\": \"in_progress\"}"
**הוספת תגובה**
curl.exe -X POST "http://127.0.0.1:8000/api/tickets/27/comments" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MjYwNzkxMn0.jmAk5ZKck_Fj0b7tJG3Kt4pF7zMEUPvGTjKyjpglV8o" -H "Content-Type: application/json" -d "{\"body\": \"Working on this fix via curl test.\"}"
**מחיקת הטיקט כמנהל**
curl.exe -X DELETE "http://127.0.0.1:8000/api/tickets/27" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MjYwNzkxMn0.jmAk5ZKck_Fj0b7tJG3Kt4pF7zMEUPvGTjKyjpglV8o"