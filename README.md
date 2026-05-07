# Real-time Collab Editor 
A real-time collaborative document editor built with FastAPI and WebSockets. Multiple users can edit documents simultaneously with live sync, AI-powered writing assistance, and document sharing between users.

## Live Demo 
https://realtime-collab-editor-oj9l.onrender.com/ 

## Tech Stack 
### Backend
- **FastAPI** - API framework
- **WebSockets** 
- **SQLAlchemy** - ORM and database modeling
- **PostgreSQL** - Database (Render)
- **Anthropic API** - AI API framework

### Frontend 
- **HTML** 
- **CSS** 
- **JavaScript** 
- **Tailwind CSS**  
- **Marked.js** - Markdown rendering for brainstorm feature 

### Deployment 
- **Render** - Web service and PostgreSQL

## Features 
- Real-time sync between clients 
- Document persistence 
- Room isolation 
- Join/disconnect notifications (with slidein/out animation)
- Active users avatar stack
- Typing indicator (with three dot load animation)
- Document title (editable, saves in real time)
- Document ownership (owner_id on Document model)
- Document sharing (invite by username, DocumentShare table)
- Share modal (owner only, username input, success/error handling)
- User owned documents + Shared documents sections on home page
- Anthropic AI assist - rewrite, expand, summarize, brainstorm 
- AI History per document 
- Context menu (right click on selected text)
- Rate limiting on AI endpoints
- Server-side ownership enforcement on rename, share, and delete (403 for non-owners)
- JWT authentication on WebSocket connections (token via query string)

## Known Limitations 
- No operational transformation (editor uses last write wins for concurrent edits)
- No cursor presence 
- No WebSocket auto-reconnect 
- Safari browser context menu compatibility issue
- Plaintext area (no rich text)

## Getting Started
**1. Clone the repo** 
```bash 
git clone https://github.com/ahuynh6265/realtime-collab-editor
cd realtime-collab-editor
``` 
**2. Install dependencies**
```bash 
pip install -r requirements.txt
```
**3. Create a .env file**
```bash
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**4. Start the server**
```bash
uvicorn main:app --reload
```

## API Endpoints 
### Landing 
|Method|Endpoint|Description|
|---|---|---|
|GET|`/`|Landing page|

### Home
|Method|Endpoint|Description|
|---|---|---|
|GET|`/home`|Shows all documents (Split between owned and shared)|

### Editor
|Method|Endpoint|Description|
|---|---|---|
|GET|`/editor`|Opens google docs-like editor|

### Documents 
|Method|Endpoint|Description|
|---|---|---|
|GET|`/documents`|List owned documents, filtered by owner_id|
|GET|`/documents/shared`|List documents shared with current user|
|POST|`/documents`|Create document and set owner_id|
|PATCH|`/documents/{document_id}`|Update title (owner only, 403 otherwise)|
|POST|`/documents/{document_id}/share`|Share with user by username (owner only; 400, 403, 404, 409 errors)|
|DELETE|`/documents/{document_id}`|Delete document and cascade related shares and AI history (owner only)|

### Authorization 
|Method|Endpoint|Description|
|---|---|---|
|GET|`/auth/login`|Login page|
|GET|`/auth/register`|Register page|
|POST|`/auth/login`|Login user returns JWT (username and id)|
|POST|`/auth/register`|Register user|
|GET|`/auth/me`|Return username|

### AI
|Method|Endpoint|Description|
|---|---|---|
|POST|`/ai/assist`|Rewrite, expand, summarize, brainstorm|
|POST|`/ai/history`|Save accepted AI action|
|GET|`/ai/history/{document_id}`|Get AI history for document|

### WebSocket
|Method|Endpoint|Description|
|---|---|---|
|WS|`/ws/{document_id}?token=<jwt>`|Establish WebSocket connection. JWT required via query string; rejects with close code 1008 if missing or invalid. Username derived from the token, not the URL.|

## Data Models

### User
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| username | String | Unique, required |
| password | String | Hashed |

### Document
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| owner_id | Integer | Foreign key → User |
| title | String | Document title |
| text | Text | Document content |
| created_at | DateTime | UTC timestamp |
| updated_at | DateTime | Auto-updates on edit |

### DocumentShare
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| document_id | Integer | Foreign key → Document |
| user_id | Integer | Foreign key → User |

### AIHistory
| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| document_id | Integer | Foreign key → Document |
| username | String | User who triggered action |
| action | String | rewrite, expand, summarize, brainstorm |
| text | String | Original text |
| ai_response | String | AI generated response |
| created_at | DateTime | UTC timestamp |
