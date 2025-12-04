from flask import Flask, request, redirect, session, render_template_string, url_for
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# === In-Memory Data ===
allowed_names = {"Rickey", "Jordan", "Uyên", "Alex", "Taylor", "Morgan"}
all_missions = [
    "Say 'It's giving Oscar energy' during a speech.",
    "Start a synchronized laugh.",
    "Reference a fake award that never happened.",
    "Convince someone to switch seats.",
    "Make a dramatic exit and casually return.",
    "Get 3 people to pose like dinosaurs.",
    "Toast to something oddly specific.",
    "Whisper 'the ducks are in formation' and walk away.",
    "Create a fake Just Side Chatting Rule.",
    "Mistake two people's names on purpose.",
    "Put a spoon in someone's pocket secretly.",
    "Teach someone a fake secret handshake."
]
assigned = {}
mission_history = []
assigned_missions = set()
unavailable_missions = set()
ADMIN_PASSWORD = 'admin123'

# === Routes & Logic (unchanged) ===
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        if name in allowed_names:
            session.clear(); session['name'] = name; session['admin'] = (name=='Uyên')
            return redirect(url_for('menu'))
        return render_template_string(LOGIN_PAGE, error='Name not found. Try again.')
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/menu', methods=['GET','POST'])
def menu():
    name = session.get('name')
    if not name: return redirect(url_for('login'))
    user = assigned.get(name)
    has = bool(user)
    can_swap = has and user['swaps']<2 and not user['completed'] and not user['failed']
    can_complete = has and not user['completed'] and not user['failed']
    can_fail = can_complete
    can_new = has and (user['completed'] or user['failed'])
    return render_template_string(MENU_PAGE, name=name, user=user, has=has,
                                  can_swap=can_swap, can_complete=can_complete,
                                  can_fail=can_fail, can_new=can_new)

@app.route('/get_mission', methods=['POST'])
def get_mission():
    name=session.get('name'); user=assigned.get(name)
    if user and not user['completed'] and not user['failed']: return redirect(url_for('menu'))
    available=[m for m in all_missions if m not in unavailable_missions]
    if not available: return render_template_string(ERROR_PAGE, message='No missions left!', back_url=url_for('menu'))
    m=random.choice(available)
    assigned[name]={'mission':m,'swaps':0,'completed':False,'failed':False,'proof':'','status':'IN PROGRESS'}
    assigned_missions.add(m); unavailable_missions.add(m)
    mission_history.append({'name':name,'mission':m,'status':'IN PROGRESS','swaps':0,'proof':''})
    return redirect(url_for('menu'))

@app.route('/swap_mission', methods=['POST'])
def swap_mission():
    name=session.get('name'); user=assigned.get(name)
    if not user or user['swaps']>=2 or user['completed'] or user['failed']: return redirect(url_for('menu'))
    old=user['mission']; assigned_missions.discard(old)
    mission_history.append({'name':name,'mission':old,'status':'SWAPPED','swaps':user['swaps'],'proof':''})
    available=[m for m in all_missions if m not in unavailable_missions]
    if not available: assigned_missions.add(old); return render_template_string(ERROR_PAGE, message='No swap options!', back_url=url_for('menu'))
    new=random.choice(available); user.update(mission=new, swaps=user['swaps']+1, status='IN PROGRESS')
    assigned_missions.add(new); unavailable_missions.add(new)
    mission_history.append({'name':name,'mission':new,'status':'IN PROGRESS','swaps':user['swaps'],'proof':''})
    return redirect(url_for('menu'))

@app.route('/complete', methods=['GET','POST'])
def complete_mission():
    name=session.get('name')
    if request.method=='POST':
        proof=request.form.get('proof'); user=assigned[name]
        user.update(completed=True, failed=False, proof=proof, status='COMPLETED')
        assigned_missions.discard(user['mission'])
        mission_history.append({'name':name,'mission':user['mission'],'status':'COMPLETED','swaps':user['swaps'],'proof':proof})
        return redirect(url_for('menu'))
    return render_template_string(COMPLETE_PAGE)

@app.route('/fail_mission', methods=['POST'])
def fail_mission():
    name=session.get('name'); user=assigned[name]
    mission_history.append({'name':name,'mission':user['mission'],'status':'FAILED','swaps':user['swaps'],'proof':''})
    assigned_missions.discard(user['mission'])
    available=[m for m in all_missions if m not in unavailable_missions]
    if not available: return render_template_string(ERROR_PAGE, message='No new missions!', back_url=url_for('menu'))
    m=random.choice(available); assigned[name]={'mission':m,'swaps':0,'completed':False,'failed':False,'proof':'','status':'IN PROGRESS'}
    assigned_missions.add(m); unavailable_missions.add(m)
    mission_history.append({'name':name,'mission':m,'status':'IN PROGRESS','swaps':0,'proof':''})
    return redirect(url_for('menu'))

@app.route('/gamemanager')
def gamemanager():
    if not session.get('admin'): return redirect(url_for('menu'))
    stats={'assigned':len(assigned_missions),'available':len(all_missions)-len(unavailable_missions),'used':len(unavailable_missions)}
    return render_template_string(GAMEMANAGER_PAGE, mission_stats=stats, assigned=assigned, mission_history=mission_history)

# === Flat UI with Bold Colors ===
BASE_CSS = '''
:root {--bg:#fafafa;--card:#ffffff;--font:'Segoe UI',Turtle, sans-serif;--primary:#ff6f61;--secondary:#6b5b95;--text:#333333;--border:#eeeeee;}
*{box-sizing:border-box;margin:0;padding:0;font-family:var(--font);color:var(--text)}
body{background:var(--bg);}
.container{width:90%;max-width:600px;margin:2rem auto;}
.card{background:var(--card);border:2px solid var(--border);border-radius:8px;padding:2rem;margin-bottom:1.5rem;}
h1,h2{margin-bottom:1rem;font-weight:700;}
input,textarea{width:100%;padding:0.75rem;border:2px solid var(--border);border-radius:4px;margin-bottom:1rem;}
button{width:100%;padding:0.75rem;border:none;border-radius:4px;background:var(--primary);color:#fff;font-size:1rem;cursor:pointer;margin-bottom:0.5rem;}
button.secondary{background:var(--secondary);}
button:disabled{background:#cccccc;cursor:not-allowed;}
a{color:var(--primary);text-decoration:none;font-weight:bold;}
a:hover{text-decoration:underline;}
table{width:100%;border-collapse:collapse;margin-bottom:1rem;}
th,td{padding:0.75rem;border:1px solid var(--border);text-align:left;}
tr:nth-child(even){background:#f5f5f5;}
'''

LOGIN_PAGE = f'''<html><head><style>{{BASE_CSS}}</style><title>Login</title></head><body>
<div class="container"><div class="card">
<h1>Login</h1>
<form method="post">
<input type="text" name="name" placeholder="Enter your name..."><button type="submit">Login</button>
</form>
{{% if error %}}<p style="color:red;">{{{{ error }}}}</p>{{% endif %}}
</div></div>
</body></html>'''

MENU_PAGE = f'''<html><head><style>{{BASE_CSS}}</style><title>Menu</title></head><body>
<div class="container"><div class="card">
<h2>Welcome, {{{{ name }}}}</h2>
{{% if has %}}
<p><strong>Mission:</strong> {{{{ user['mission'] }}}}</p>
<p><strong>Status:</strong> {{{{ user['status'] }}}}</p>
<p><strong>Swaps:</strong> {{{{ user['swaps'] }}}}/2</p>
{{% else %}}<p>No mission assigned.</p>{{% endif %}}
<form method="post" action="/get_mission"><button>Get Mission</button></form>
<form method="post" action="/swap_mission"><button class="secondary" {{% if not can_swap %}}disabled{{% endif %}}>Swap Mission</button></form>
<form method="post" action="/fail_mission"><button class="secondary" {{% if not can_fail %}}disabled{{% endif %}}>Fail Mission</button></form>
<form method="get" action="/complete"><button {{% if not can_complete %}}disabled{{% endif %}}>Complete Mission</button></form>
</div></div>
</body></html>'''

COMPLETE_PAGE = f'''<html><head><style>{{BASE_CSS}}</style><title>Complete</title></head><body>
<div class="container"><div class="card">
<h2>Submit Proof</h2>
<form method="post">
<textarea name="proof" placeholder="Describe completion..."></textarea>
<button>Submit</button>
</form>
<a href="/menu">Back to Menu</a>
</div></div>
</body></html>'''

ERROR_PAGE = f'''<html><head><style>{{BASE_CSS}}</style><title>Error</title></head><body>
<div class="container"><div class="card">
<h2 style="color:red;">Error</h2>
<p>{{{{ message }}}}</p>
<a href="{{{{ back_url }}}}">Back</a>
</div></div>
</body></html>'''

GAMEMANAGER_PAGE = f'''<html><head><style>{{BASE_CSS}}</style><title>Manager</title></head><body>
<div class="container"><div class="card">
<h2>Game Manager Control Panel</h2>
<p><strong>Assigned:</strong> {{{{ mission_stats['assigned'] }}}} | <strong>Available:</strong> {{{{ mission_stats['available'] }}}} | <strong>Used:</strong> {{{{ mission_stats['used'] }}}}</p>
</div><div class="card">
<h2>Current Status</h2>
<table><tr><th>Name</th><th>Mission</th><th>Swaps</th><th>Status</th><th>Proof</th></tr>
{{% for name,data in assigned.items() %}}<tr><td>{{{{ name }}}}</td><td>{{{{ data['mission'] }}}}</td><td>{{{{ data['swaps'] }}}}/2</td><td>{{{{ data['status'] }}}}</td><td>{{{{ data['proof'] }}}}</td></tr>{{% endfor %}}</table>
</div><div class="card">
<h2>Mission History</h2>
<table><tr><th>Name</th><th>Mission</th><th>Status</th><th>Swaps</th><th>Proof</th></tr>
{{% for e in mission_history %}}<tr><td>{{{{ e['name'] }}}}</td><td>{{{{ e['mission'] }}}}</td><td>{{{{ e['status'] }}}}</td><td>{{{{ e['swaps'] }}}}/2</td><td>{{{{ e['proof'] }}}}</td></tr>{{% endfor %}}</table>
</div><a href="/menu" style="display:block;text-align:center;background:var(--primary);color:#fff;padding:0.75rem;border:none;border-radius:4px;text-decoration:none;">Back to Menu</a>
</div></body></html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
