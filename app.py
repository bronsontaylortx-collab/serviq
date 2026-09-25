<!doctype html>
<html>
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>Calls | ServIQ</title>

<style>

*{box-sizing:border-box}

:root{
--navy:#071426;
--navy2:#0b1d35;
--blue:#3b82f6;
--purple:#8b5cf6;
--green:#16a34a;
--red:#ef4444;
--orange:#f59e0b;
--bg:#f3f6fb;
--text:#142033;
--muted:#718096;
--border:#e3e9f2;
}

body{
margin:0;
background:var(--bg);
color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}

header{
background:
radial-gradient(circle at 80% -40%,#174e91 0%,transparent 45%),
linear-gradient(135deg,#071426,#0b1d35);
color:white;
padding:22px 18px 0;
}

.header-inner{
max-width:1180px;
margin:auto;
}

.brand-row{
display:flex;
justify-content:space-between;
align-items:center;
}

.logo-wrap{
display:flex;
align-items:center;
gap:11px;
}

.logo{
width:42px;
height:42px;
border-radius:12px;
display:flex;
align-items:center;
justify-content:center;
font-weight:900;
font-size:20px;
background:linear-gradient(135deg,#3b82f6,#7c3aed);
box-shadow:0 8px 24px rgba(59,130,246,.35);
}

.brand{
font-size:26px;
font-weight:850;
}

.sub{
color:#94a3b8;
font-size:12px;
margin-top:2px;
}

.live{
background:rgba(34,197,94,.12);
color:#86efac;
border:1px solid rgba(34,197,94,.25);
padding:7px 11px;
border-radius:999px;
font-size:11px;
font-weight:800;
}

.nav{
display:flex;
gap:5px;
margin-top:22px;
overflow-x:auto;
scrollbar-width:none;
}

.nav::-webkit-scrollbar{display:none}

.nav a{
color:#94a3b8;
text-decoration:none;
padding:12px 14px;
font-size:13px;
font-weight:750;
white-space:nowrap;
border-bottom:3px solid transparent;
}

.nav a.active{
color:white;
border-bottom-color:#3b82f6;
}

main{
max-width:1180px;
margin:auto;
padding:22px 16px;
}

.page-title{
font-size:27px;
font-weight:850;
letter-spacing:-.6px;
}

.page-sub{
font-size:13px;
color:#718096;
margin-top:4px;
}

.summary{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:12px;
margin:20px 0;
}

.summary-card{
background:white;
border:1px solid var(--border);
border-radius:16px;
padding:17px;
}

.summary-label{
font-size:10px;
font-weight:850;
color:#7b8798;
letter-spacing:.5px;
}

.summary-number{
font-size:26px;
font-weight:850;
margin-top:5px;
}

.filters{
background:white;
border:1px solid var(--border);
border-radius:16px;
padding:14px;
margin-bottom:15px;
}

.search{
width:100%;
padding:13px 14px;
border:1px solid #d8e0ea;
border-radius:10px;
font-size:14px;
outline:none;
}

.search:focus{
border-color:#3b82f6;
box-shadow:0 0 0 3px rgba(59,130,246,.1);
}

.filter-row{
display:flex;
gap:7px;
margin-top:10px;
overflow-x:auto;
}

.filter{
border:1px solid #dce3ec;
background:#f8fafc;
color:#5f6c80;
padding:8px 11px;
border-radius:999px;
font-size:11px;
font-weight:800;
text-decoration:none;
white-space:nowrap;
}

.filter.active{
background:#2563eb;
color:white;
border-color:#2563eb;
}

.call-card{
background:white;
border:1px solid var(--border);
border-radius:17px;
padding:17px;
margin-bottom:12px;
box-shadow:0 3px 12px rgba(15,23,42,.025);
}

.call-top{
display:flex;
justify-content:space-between;
align-items:flex-start;
gap:10px;
}

.agent{
font-size:16px;
font-weight:850;
}

.call-id{
font-size:11px;
color:#8793a5;
margin-top:3px;
}

.score{
width:55px;
height:55px;
border-radius:15px;
display:flex;
align-items:center;
justify-content:center;
font-size:17px;
font-weight:900;
background:#eef4ff;
color:#2563eb;
}

.score.bad{
background:#feecec;
color:#dc2626;
}

.details{
display:grid;
grid-template-columns:1fr 1fr;
gap:12px;
margin:15px 0;
padding:14px 0;
border-top:1px solid #edf1f5;
border-bottom:1px solid #edf1f5;
}

.detail-label{
font-size:9px;
font-weight:850;
color:#8a96a8;
letter-spacing:.5px;
}

.detail-value{
font-size:12px;
font-weight:750;
margin-top:3px;
}

.status{
display:inline-block;
padding:6px 9px;
border-radius:999px;
font-size:10px;
font-weight:850;
}

.status.pass{
background:#e8f7ed;
color:#087443;
}

.status.review{
background:#fff4dd;
color:#a15c00;
}

.status.critical{
background:#fee7e7;
color:#c62828;
}

.card-footer{
display:flex;
justify-content:space-between;
align-items:center;
gap:10px;
}

.time{
font-size:11px;
color:#8491a5;
}

.review-button{
text-decoration:none;
background:linear-gradient(90deg,#2563eb,#4f46e5);
color:white;
padding:9px 12px;
border-radius:9px;
font-size:11px;
font-weight:850;
}

.empty{
background:white;
border:1px solid var(--border);
border-radius:16px;
padding:35px 20px;
text-align:center;
color:#718096;
}

@media(min-width:800px){

.call-list{
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
}

.call-card{
margin-bottom:0;
}

}

@media(max-width:600px){

.summary{
grid-template-columns:1fr 1fr 1fr;
gap:8px;
}

.summary-card{
padding:13px;
}

.summary-number{
font-size:22px;
}

main{
padding:18px 12px;
}

}

</style>
</head>


<body>

<header>

<div class="header-inner">

<div class="brand-row">

<div class="logo-wrap">

<div class="logo">S</div>

<div>
<div class="brand">ServIQ</div>
<div class="sub">AI Quality Assurance for Mortgage Servicing</div>
</div>

</div>

<div class="live">● AI ONLINE</div>

</div>


<nav class="nav">

<a href="/">Dashboard</a>

<a class="active" href="/calls">Calls</a>

<a href="#">Scorecards</a>

<a href="#">Coaching</a>

<a href="#">Analytics</a>

<a href="#">Team</a>

</nav>

</div>

</header>


<main>

<div class="page-title">Calls</div>

<div class="page-sub">
AI-analyzed mortgage servicing conversations
</div>


<div class="summary">

<div class="summary-card">
<div class="summary-label">TODAY</div>
<div class="summary-number">248</div>
</div>

<div class="summary-card">
<div class="summary-label">REVIEW</div>
<div class="summary-number">42</div>
</div>

<div class="summary-card">
<div class="summary-label">CRITICAL</div>
<div class="summary-number">18</div>
</div>

</div>


<div class="filters">

<form method="get" action="/calls">

<input
class="search"
type="search"
name="search"
value="{{ search }}"
placeholder="Search agent, team, call ID or call type..."
>

</form>


<div class="filter-row">

<a
class="filter {% if selected_status == 'All' %}active{% endif %}"
href="/calls">
All Calls
</a>

<a
class="filter {% if selected_status == 'Needs Review' %}active{% endif %}"
href="/calls?status=Needs+Review">
Needs Review
</a>

<a
class="filter {% if selected_status == 'Critical' %}active{% endif %}"
href="/calls?status=Critical">
Critical
</a>

<a
class="filter {% if selected_status == 'Passed' %}active{% endif %}"
href="/calls?status=Passed">
Passed
</a>

</div>

</div>


<div class="call-list">

{% for call in calls %}

<div class="call-card">

<div class="call-top">

<div>

<div class="agent">
{{ call.agent }}
</div>

<div class="call-id">
{{ call.id }} · {{ call.duration }}
</div>

</div>


<div class="score {% if call.score < 70 %}bad{% endif %}">
{{ call.score }}
</div>

</div>


<div class="details">

<div>

<div class="detail-label">
TEAM
</div>

<div class="detail-value">
{{ call.team }}
</div>

</div>


<div>

<div class="detail-label">
CALL TYPE
</div>

<div class="detail-value">
{{ call.call_type }}
</div>

</div>


<div>

<div class="detail-label">
AI CONFIDENCE
</div>

<div class="detail-value">
{{ call.confidence }}%
</div>

</div>


<div>

<div class="detail-label">
STATUS
</div>

<div class="detail-value">

{% if call.status == "Critical" %}

<span class="status critical">
Critical Failure
</span>

{% elif call.status == "Needs Review" %}

<span class="status review">
Needs Review
</span>

{% else %}

<span class="status pass">
Passed
</span>

{% endif %}

</div>

</div>

</div>


<div class="card-footer">

<div class="time">
{{ call.time }}
</div>

<a
class="review-button"
href="/calls/{{ call.id }}"
>
Review Call →
</a>

</div>

</div>

{% else %}

<div class="empty">
No calls match your filters.
</div>

{% endfor %}

</div>

</main>

</body>
</html>
