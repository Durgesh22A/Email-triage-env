from flask import Flask, render_template_string, jsonify
import os
import json
import base64
from openai import OpenAI
from gmail_fetcher import get_gmail_service

app = Flask(__name__)

client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.environ.get("HF_TOKEN", ""),
)
MODEL = os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")

email_cache = []
cache_loaded = False

def categorize_email(email):
    prompt = f"""You are an email triage assistant.
Email:
- Subject: {email['subject']}
- From: {email['sender']}
- Body: {email['body'][:300]}

Respond ONLY with JSON:
{{
  "priority": "urgent" or "normal" or "low",
  "category": "support" or "sales" or "spam" or "hr" or "newsletter" or "personal" or "tech",
  "action": "reply" or "forward" or "archive" or "delete",
  "reason": "one line explanation"
}}"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"priority": "normal", "category": "personal", "action": "archive", "reason": "Could not categorize"}

def get_email_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                d = part['body'].get('data', '')
                if d:
                    body = base64.urlsafe_b64decode(d).decode('utf-8', errors='ignore')
                    break
    else:
        d = payload['body'].get('data', '')
        if d:
            body = base64.urlsafe_b64decode(d).decode('utf-8', errors='ignore')
    return body.strip()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>📧 Email Triage Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #fff; padding: 20px; }
        h1 { text-align: center; margin-bottom: 10px; font-size: 2em; color: #7c6af7; }
        .refresh-bar { text-align: center; margin-bottom: 20px; color: #888; display: flex; align-items: center; justify-content: center; gap: 15px; }
        #countdown { color: #7c6af7; font-weight: bold; }
        .btn { padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; font-size: 0.9em; font-weight: bold; }
        .btn-refresh { background: #7c6af7; color: white; }
        .stats { display: flex; gap: 15px; margin-bottom: 20px; justify-content: center; flex-wrap: wrap; }
        .stat-card { background: #1a1a2e; border-radius: 12px; padding: 15px 25px; text-align: center; border: 1px solid #2a2a4a; min-width: 100px; }
        .stat-card h2 { font-size: 2em; color: #7c6af7; }
        .stat-card p { color: #888; margin-top: 5px; font-size: 0.85em; }
        .filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center; }
        .filter-btn { padding: 6px 16px; border-radius: 20px; border: 2px solid #2a2a4a; background: #1a1a2e; color: #888; cursor: pointer; font-size: 0.85em; transition: all 0.2s; }
        .filter-btn:hover { border-color: #7c6af7; color: #fff; }
        .filter-btn.active { background: #7c6af7; border-color: #7c6af7; color: #fff; }
        .search-bar { width: 100%; max-width: 400px; display: block; margin: 0 auto 20px; padding: 10px 15px; border-radius: 8px; border: 1px solid #2a2a4a; background: #1a1a2e; color: #fff; font-size: 0.95em; }
        .search-bar:focus { outline: none; border-color: #7c6af7; }
        .email-count { text-align: center; color: #888; margin-bottom: 15px; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 12px; overflow: hidden; }
        th { background: #2a2a4a; padding: 15px; text-align: left; color: #7c6af7; }
        td { padding: 12px 15px; border-bottom: 1px solid #2a2a4a; vertical-align: top; }
        tr:hover { background: #252540; }
        .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; white-space: nowrap; }
        .urgent { background: #ff4444; color: white; }
        .normal { background: #4444ff; color: white; }
        .low { background: #44aa44; color: white; }
        .support { background: #ff8800; color: white; }
        .spam { background: #ff4444; color: white; }
        .tech { background: #0088ff; color: white; }
        .newsletter { background: #8800ff; color: white; }
        .personal { background: #00aa88; color: white; }
        .sales { background: #ff6600; color: white; }
        .hr { background: #aa0088; color: white; }
        .reply { background: #00aa44; color: white; }
        .archive { background: #888800; color: white; }
        .delete { background: #aa0000; color: white; }
        .forward { background: #0088aa; color: white; }
        .subject { font-weight: bold; max-width: 250px; }
        .sender { color: #888; font-size: 0.85em; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .reason { color: #aaa; font-size: 0.82em; max-width: 220px; }
        .loading-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,15,26,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 999; }
        .loading-overlay h2 { color: #7c6af7; margin-bottom: 15px; }
        .loading-overlay p { color: #888; }
        .spinner { width: 50px; height: 50px; border: 4px solid #2a2a4a; border-top: 4px solid #7c6af7; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .no-results { text-align: center; padding: 40px; color: #888; }
    </style>
</head>
<body>

<div class="loading-overlay" id="loadingOverlay">
    <div class="spinner"></div>
    <h2>📧 Fetching Emails...</h2>
    <p id="loadingText">Connecting to Gmail...</p>
</div>

<h1>📧 Email Triage Dashboard</h1>

<div class="refresh-bar">
    <span>Auto-refresh in <span id="countdown">300</span>s</span>
    <button class="btn btn-refresh" onclick="refreshNow()">🔄 Refresh Now</button>
    <span id="lastUpdated" style="color:#555">Never updated</span>
</div>

<div class="stats">
    <div class="stat-card"><h2 id="statTotal">-</h2><p>Total Emails</p></div>
    <div class="stat-card"><h2 id="statUrgent">-</h2><p>Urgent</p></div>
    <div class="stat-card"><h2 id="statSpam">-</h2><p>Spam</p></div>
    <div class="stat-card"><h2 id="statReply">-</h2><p>Need Reply</p></div>
    <div class="stat-card"><h2 id="statSupport">-</h2><p>Support</p></div>
    <div class="stat-card"><h2 id="statNewsletter">-</h2><p>Newsletter</p></div>
</div>

<div class="filters">
    <button class="filter-btn active" onclick="filterEmails('all', this)">All</button>
    <button class="filter-btn" onclick="filterEmails('urgent', this)">🔴 Urgent</button>
    <button class="filter-btn" onclick="filterEmails('support', this)">🛠 Support</button>
    <button class="filter-btn" onclick="filterEmails('tech', this)">💻 Tech</button>
    <button class="filter-btn" onclick="filterEmails('newsletter', this)">📰 Newsletter</button>
    <button class="filter-btn" onclick="filterEmails('spam', this)">🚫 Spam</button>
    <button class="filter-btn" onclick="filterEmails('personal', this)">👤 Personal</button>
    <button class="filter-btn" onclick="filterEmails('sales', this)">💰 Sales</button>
    <button class="filter-btn" onclick="filterEmails('hr', this)">👥 HR</button>
    <button class="filter-btn" onclick="filterEmails('reply', this)">💬 Need Reply</button>
</div>

<input type="text" class="search-bar" id="searchBox" placeholder="🔍 Search emails..." oninput="searchEmails()">
<div class="email-count" id="emailCount"></div>

<table>
    <thead>
        <tr>
            <th>📩 Subject</th>
            <th>👤 Sender</th>
            <th>🏷️ Category</th>
            <th>⚡ Priority</th>
            <th>✅ Action</th>
            <th>💡 Reason</th>
        </tr>
    </thead>
    <tbody id="emailBody">
        <tr><td colspan="6" class="no-results">Loading emails...</td></tr>
    </tbody>
</table>

<script>
let allEmails = [];
let currentFilter = 'all';
let countdownVal = 300;
let countdownTimer;

async function loadEmails() {
    document.getElementById('loadingOverlay').style.display = 'flex';
    try {
        const res = await fetch('/api/emails');
        allEmails = await res.json();
        renderEmails(allEmails);
        updateStats(allEmails);
        document.getElementById('lastUpdated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
    } catch(e) {
        document.getElementById('emailBody').innerHTML = '<tr><td colspan="6" class="no-results">Error loading. Try refreshing.</td></tr>';
    }
    document.getElementById('loadingOverlay').style.display = 'none';
    resetCountdown();
}

function renderEmails(emails) {
    const tbody = document.getElementById('emailBody');
    document.getElementById('emailCount').textContent = `Showing ${emails.length} emails`;
    if (emails.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-results">No emails found</td></tr>';
        return;
    }
    tbody.innerHTML = emails.map(e => `
        <tr>
            <td class="subject">${e.subject.substring(0,60)}</td>
            <td class="sender">${e.sender.substring(0,40)}</td>
            <td><span class="badge ${e.result.category}">${e.result.category}</span></td>
            <td><span class="badge ${e.result.priority}">${e.result.priority}</span></td>
            <td><span class="badge ${e.result.action}">${e.result.action}</span></td>
            <td class="reason">${e.result.reason}</td>
        </tr>
    `).join('');
}

function updateStats(emails) {
    document.getElementById('statTotal').textContent = emails.length;
    document.getElementById('statUrgent').textContent = emails.filter(e => e.result.priority === 'urgent').length;
    document.getElementById('statSpam').textContent = emails.filter(e => e.result.category === 'spam').length;
    document.getElementById('statReply').textContent = emails.filter(e => e.result.action === 'reply').length;
    document.getElementById('statSupport').textContent = emails.filter(e => e.result.category === 'support').length;
    document.getElementById('statNewsletter').textContent = emails.filter(e => e.result.category === 'newsletter').length;
}

function filterEmails(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    let filtered;
    if (filter === 'all') filtered = allEmails;
    else if (filter === 'urgent') filtered = allEmails.filter(e => e.result.priority === 'urgent');
    else if (filter === 'reply') filtered = allEmails.filter(e => e.result.action === 'reply');
    else filtered = allEmails.filter(e => e.result.category === filter);
    const search = document.getElementById('searchBox').value.toLowerCase();
    if (search) filtered = filtered.filter(e => e.subject.toLowerCase().includes(search) || e.sender.toLowerCase().includes(search));
    renderEmails(filtered);
}

function searchEmails() {
    const search = document.getElementById('searchBox').value.toLowerCase();
    let filtered = allEmails;
    if (currentFilter !== 'all') {
        if (currentFilter === 'urgent') filtered = allEmails.filter(e => e.result.priority === 'urgent');
        else if (currentFilter === 'reply') filtered = allEmails.filter(e => e.result.action === 'reply');
        else filtered = allEmails.filter(e => e.result.category === currentFilter);
    }
    if (search) filtered = filtered.filter(e => e.subject.toLowerCase().includes(search) || e.sender.toLowerCase().includes(search));
    renderEmails(filtered);
}

async function refreshNow() {
    await fetch('/api/refresh');
    loadEmails();
}

function resetCountdown() {
    clearInterval(countdownTimer);
    countdownVal = 300;
    document.getElementById('countdown').textContent = countdownVal;
    countdownTimer = setInterval(() => {
        countdownVal--;
        document.getElementById('countdown').textContent = countdownVal;
        if (countdownVal <= 0) {
            clearInterval(countdownTimer);
            loadEmails();
        }
    }, 1000);
}

loadEmails();
</script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML)

@app.route('/api/refresh')
def force_refresh():
    global cache_loaded
    cache_loaded = False
    return jsonify({"status": "cache cleared"})

@app.route('/api/emails')
def get_emails():
    global email_cache, cache_loaded
    if cache_loaded and email_cache:
        return jsonify(email_cache)

    print("Fetching ALL emails from Gmail...")
    service = get_gmail_service()
    all_messages = []
    request = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=500)
    while request is not None:
        result = request.execute()
        all_messages.extend(result.get('messages', []))
        request = service.users().messages().list_next(request, result)
        if len(all_messages) >= 500:
            break

    print(f"Total: {len(all_messages)} emails")
    enriched = []
    for i, msg in enumerate(all_messages):
        try:
            data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            body = get_email_body(data['payload'])
            result = categorize_email({"subject": subject, "sender": sender, "body": body})
            enriched.append({"subject": subject, "sender": sender, "result": result})
            print(f"[{i+1}/{len(all_messages)}] ✅ {subject[:40]}")
        except Exception as ex:
            print(f"Error: {ex}")
            continue

    email_cache = enriched
    cache_loaded = True
    return jsonify(enriched)

if __name__ == "__main__":
    app.run(debug=True, port=5000)