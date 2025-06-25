from flask import Flask, render_template_string, request, redirect, url_for, session
import random
import time
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'countdown_secret_key'
LEADERBOARD_FILE = 'leaderboard.json'
SETTINGS_FILE = 'settings.json'
GLOBAL_SETTINGS_FILE = 'global_settings.json'

def ensure_leaderboard_file():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump([], f)

def get_leaderboard():
    ensure_leaderboard_file()
    with open(LEADERBOARD_FILE, 'r') as f:
        try:
            leaderboard = json.load(f)
        except json.JSONDecodeError:
            leaderboard = []
    leaderboard.sort(key=lambda x: x['score'])
    return leaderboard

def save_to_leaderboard(player, score, difficulty, mode):
    ensure_leaderboard_file()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = {
        'player': player,
        'score': round(score, 3),
        'difficulty': difficulty,
        'mode': mode,
        'date': timestamp
    }
    leaderboard = get_leaderboard()
    leaderboard.append(entry)
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f, indent=2)

def get_difficulty_range(difficulty):
    if difficulty == 'easy':
        return (5, 10)
    elif difficulty == 'medium':
        return (3, 15)
    else:
        return (1, 20)

def load_settings(player):
    if not os.path.exists(SETTINGS_FILE):
        return None
    with open(SETTINGS_FILE, 'r') as f:
        try:
            all_settings = json.load(f)
        except json.JSONDecodeError:
            all_settings = {}
    return all_settings.get(player)

def save_settings(player, mode, difficulty):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            try:
                all_settings = json.load(f)
            except json.JSONDecodeError:
                all_settings = {}
    else:
        all_settings = {}
    all_settings[player] = {'mode': mode, 'difficulty': difficulty}
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(all_settings, f, indent=2)

def load_global_settings():
    if not os.path.exists(GLOBAL_SETTINGS_FILE):
        return {'target_time': 5.0, 'mode': 'hidden'}
    with open(GLOBAL_SETTINGS_FILE, 'r') as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            settings = {'target_time': 5.0, 'mode': 'hidden'}
    if 'target_time' not in settings:
        settings['target_time'] = 5.0
    if 'mode' not in settings:
        settings['mode'] = 'hidden'
    return settings

def save_global_settings(target_time, mode):
    with open(GLOBAL_SETTINGS_FILE, 'w') as f:
        json.dump({'target_time': target_time, 'mode': mode}, f, indent=2)

# HTML template (inline for simplicity)
TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Leet Precision Game</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #181c20; color: #e0e0e0; font-family: 'Fira Mono', monospace; margin: 0; }
        .container { display: flex; min-height: 100vh; }
        .main { flex: 2; padding: 40px; }
        .sidebar { flex: 1; background: #23272b; padding: 40px 20px; border-left: 2px solid #2e3236; }
        h1, h2 { color: #00ffe7; letter-spacing: 2px; }
        .techy-box { background: #23272b; border: 1px solid #00ffe7; border-radius: 8px; padding: 24px; margin-bottom: 32px; box-shadow: 0 0 12px #00ffe733; }
        .button { background: #00ffe7; color: #181c20; border: none; padding: 12px 32px; border-radius: 6px; font-size: 1.1em; cursor: pointer; margin: 8px 0; transition: background 0.2s; }
        .button:hover { background: #00bfae; }
        .input { background: #181c20; color: #00ffe7; border: 1px solid #00ffe7; border-radius: 4px; padding: 8px 12px; font-size: 1em; }
        .leaderboard-table { width: 100%; border-collapse: collapse; }
        .leaderboard-table th, .leaderboard-table td { padding: 6px 8px; text-align: left; }
        .leaderboard-table th { color: #00ffe7; border-bottom: 1px solid #00ffe7; }
        .leaderboard-table tr:nth-child(even) { background: #202428; }
        .timer-bar-bg { background: #23272b; border-radius: 8px; height: 32px; width: 100%; margin: 16px 0; }
        .timer-bar { background: #00ffe7; height: 100%; border-radius: 8px; transition: width 0.1s; }
        .feedback { font-size: 1.2em; margin: 16px 0; }
        .sysinfo { color: #00ffe7; font-size: 0.95em; margin-bottom: 18px; }
        @media (max-width: 900px) {
            .container { flex-direction: column; }
            .sidebar { border-left: none; border-top: 2px solid #2e3236; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="main">
        <h1>Count It Down!</h1>
        {% if not session.player %}
            <div class="techy-box">
                <h2>Register Player</h2>
                <form method="post" action="{{ url_for('register') }}">
                    <input class="input" type="text" name="player" placeholder="Enter your name" required maxlength="20">
                    <button class="button" type="submit">Register</button>
                </form>
            </div>
        {% elif not session.get('playing') %}
            <div class="techy-box">
                <h2>Main Menu</h2>
                <form method="post" action="{{ url_for('start_game') }}">
                    <button class="button" type="submit">Play Game</button>
                </form>
                <form method="get" action="{{ url_for('settings') }}">
                    <button class="button" type="submit">Settings</button>
                </form>
                <form method="get" action="{{ url_for('logout') }}">
                    <button class="button" type="submit">Change Player</button>
                </form>
            </div>
        {% elif session.get('playing') %}
            <div class="techy-box">
                <h2>Timer Running</h2>
                <div class="sysinfo">
                    [MODE] {{ global_settings.mode|upper }} | [TARGET] {% if global_settings.mode == 'visible' %}{{ session.target_time|round(3) }}s{% else %}Hidden{% endif %}
                </div>
                <form id="stop-form" method="post" action="{{ url_for('stop_game') }}">
                    <input type="hidden" name="start_time" value="{{ session.start_time }}">
                    <button class="button" type="submit" id="stop-btn">Stop Timer</button>
                </form>
                <div class="timer-bar-bg">
                    <div class="timer-bar" id="timer-bar" style="width:0%"></div>
                </div>
                <div id="timer-elapsed" style="color:#00ffe7; font-size:1.1em;"></div>
            </div>
            <script>
                let start = Date.now();
                let running = true;
                let target = {{ session.target_time }};
                function updateBar() {
                    if (!running) return;
                    let elapsed = (Date.now() - start) / 1000;
                    let percent = Math.min(100, (elapsed / target) * 100);
                    document.getElementById('timer-bar').style.width = percent + '%';
                    document.getElementById('timer-elapsed').innerText = 'Elapsed: ' + elapsed.toFixed(3) + 's';
                    requestAnimationFrame(updateBar);
                }
                updateBar();
                // Spacebar triggers stop
                document.addEventListener('keydown', function(e) {
                    if (e.code === 'Space' && running) {
                        running = false;
                        document.getElementById('stop-form').submit();
                    }
                });
            </script>
        {% endif %}
        {% if session.get('result') %}
            <div class="techy-box">
                <h2>Results</h2>
                <div class="sysinfo">Target: {{ session.result.target|round(3) }}s | You: {{ session.result.elapsed|round(3) }}s | Diff: {{ session.result.diff|round(3) }}s</div>
                <div class="feedback" style="color:#00ffe7;">{{ session.result.feedback }}</div>
                <form method="post" action="{{ url_for('clear_result') }}">
                    <button class="button" type="submit">Back to Menu</button>
                </form>
            </div>
        {% endif %}
        {% if settings %}
            <div class="techy-box">
                <h2>Settings</h2>
                <form method="post" action="{{ url_for('settings') }}">
                    <label>Target Visibility:</label>
                    <select class="input" name="mode">
                        <option value="hidden" {% if global_settings.mode == 'hidden' %}selected{% endif %}>Hidden</option>
                        <option value="visible" {% if global_settings.mode == 'visible' %}selected{% endif %}>Visible</option>
                    </select><br><br>
                    <label>Target Time (seconds):</label>
                    <input class="input" type="number" step="0.01" min="0.01" name="target_time" value="{{ global_settings.target_time }}" required><br><br>
                    <button class="button" type="submit">Save</button>
                </form>
                <form method="get" action="{{ url_for('index') }}">
                    <button class="button" type="submit">Back</button>
                </form>
            </div>
        {% endif %}
    </div>
    <div class="sidebar">
        <h2>Leaderboard</h2>
        <table class="leaderboard-table">
            <tr><th>Rank</th><th>Player</th><th>Score</th></tr>
            {% for entry in leaderboard[:10] %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ entry.player }}</td>
                <td>{{ entry.score|round(3) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    leaderboard = get_leaderboard()
    global_settings = load_global_settings()
    settings = False
    return render_template_string(TEMPLATE, leaderboard=leaderboard, settings=settings, global_settings=global_settings)

@app.route('/register', methods=['POST'])
def register():
    session['player'] = request.form['player']
    session['playing'] = False
    session.pop('result', None)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/start_game', methods=['POST'])
def start_game():
    if not session.get('player'):
        return redirect(url_for('index'))
    global_settings = load_global_settings()
    target_time = float(global_settings.get('target_time', 5.0))
    session['target_time'] = target_time
    session['start_time'] = time.time()
    session['playing'] = True
    session.pop('result', None)
    return redirect(url_for('index'))

@app.route('/stop_game', methods=['POST'])
def stop_game():
    if not session.get('playing'):
        return redirect(url_for('index'))
    elapsed = time.time() - session['start_time']
    target = session['target_time']
    diff = abs(elapsed - target)
    feedback = get_feedback(diff)
    global_settings = load_global_settings()
    save_to_leaderboard(session['player'], diff, None, global_settings['mode'])
    session['result'] = {'target': target, 'elapsed': elapsed, 'diff': diff, 'feedback': feedback}
    session['playing'] = False
    return redirect(url_for('index'))

def get_feedback(difference):
    if difference <= 0.05:
        return "🎯 PERFECT HIT! You're a timing master! 🎯"
    elif difference <= 0.1:
        return "👍 EXCELLENT! Incredible precision! 👍"
    elif difference <= 0.2:
        return "👏 GREAT JOB! Very close! 👏"
    elif difference <= 0.3:
        return "🔔 Good effort! Within 0.3 seconds 🔔"
    elif difference <= 0.5:
        return "✨ Not bad! Practice makes perfect ✨"
    else:
        return "💤 Missed! Keep trying! 💤"

@app.route('/clear_result', methods=['POST'])
def clear_result():
    session.pop('result', None)
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global_settings = load_global_settings()
    if request.method == 'POST':
        # Save global target time and mode
        try:
            target_time = float(request.form['target_time'])
            mode = request.form['mode']
            save_global_settings(target_time, mode)
        except ValueError:
            pass
        return redirect(url_for('index'))
    leaderboard = get_leaderboard()
    settings = True
    return render_template_string(TEMPLATE, leaderboard=leaderboard, settings=settings, global_settings=global_settings)

if __name__ == '__main__':
    ensure_leaderboard_file()
    app.run(debug=True) 
