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
