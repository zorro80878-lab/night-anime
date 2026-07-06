from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# آدرس سرور اسکرپر اصلی با لایه پشتیبان در صورت قطعی
BASE_API = "https://consumet.org"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Night Anime | پخش آنلاین خودکار</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0a0a0c; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: #111115; padding: 25px; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.8); }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #222; padding-bottom: 15px; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
        .logo { font-size: 26px; font-weight: bold; color: #ff793f; text-decoration: none; }
        .logo span { color: #fff; }
        .search-form input { padding: 12px 20px; border-radius: 20px; border: 1px solid #333; background: #1a1a22; color: white; width: 250px; outline: none; }
        .search-form input:focus { border-color: #ff793f; }
        .player-box { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 8px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 0 20px rgba(255,121,63,0.15); }
        iframe { width: 100%; height: 100%; border: none; }
        .ep-list { display: flex; flex-wrap: wrap; gap: 8px; background: #161622; padding: 15px; border-radius: 8px; max-height: 150px; overflow-y: auto; }
        .ep-btn { background: #252533; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 14px; transition: 0.2s; }
        .ep-btn:hover { background: #38384d; }
        .ep-btn.active { background: linear-gradient(135deg, #ff793f, #ffb142); color: black; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; }
        .anime-card { background: #181822; border-radius: 8px; overflow: hidden; text-align: center; text-decoration: none; color: white; transition: 0.3s; border: 1px solid #222; }
        .anime-card:hover { transform: translateY(-5px); border-color: #ff793f; }
        .anime-card img { width: 100%; height: 220px; object-fit: cover; }
        .anime-card p { padding: 10px; font-size: 14px; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="/" class="logo">Night <span>Anime</span> •</a>
            <form action="/" method="GET" class="search-form">
                <input type="text" name="search" placeholder="جستجوی انیمه (به انگلیسی)..." required>
            </form>
        </header>

        {% if view == 'player' %}
            <h2>🍿 در حال تماشای: {{ title }} - قسمت {{ current_ep }}</h2>
            <div class="player-box">
                {% if video_url %}
                    <iframe src="{{ video_url }}" allowfullscreen="true" scrolling="no"></iframe>
                {% else %}
                    <p style="text-align:center; padding-top:20%;">⚠️ سرور پخش ویدیو پاسخ نمی‌دهد یا این قسمت در دسترس نیست.</p>
                {% endif %}
            </div>
            <h3>🎞️ انتخاب قسمت:</h3>
            <div class="ep-list">
                {% for ep in episodes %}
                    <a href="/watch?id={{ anime_id }}&ep={{ ep }}" class="ep-btn {% if ep == current_ep %}active{% endif %}">قسمت {{ ep }}</a>
                {% endfor %}
            </div>
        {% else %}
            <h2>{{ section_title }}</h2>
            <div class="grid">
                {% for anime in results %}
                    <a href="/watch?id={{ anime.id }}&ep=1" class="anime-card">
                        <img src="{{ anime.image }}" alt="پوستر">
                        <p>{{ anime.title }}</p>
                    </a>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    search_query = request.args.get('search')
    if search_query:
        url = f"{BASE_API}/{search_query}"
        section_title = f"🔍 نتایج جستجو برای: {search_query}"
    else:
        url = f"{BASE_API}/top-airing"
        section_title = "🔥 انیمه‌های جدید و محبوب در حال پخش"
        
    try:
        res = requests.get(url, timeout=7)
        results = res.json().get('results', []) if res.status_code == 200 else []
    except:
        results = []
        
    return render_template_string(HTML_TEMPLATE, view='home', results=results, section_title=section_title)

@app.route('/watch')
def watch():
    anime_id = request.args.get('id')
    current_ep = request.args.get('ep', default=1, type=int)
    video_url, episodes, title = "", [], "انیمه"
    
    try:
        info_res = requests.get(f"{BASE_API}/info/{anime_id}", timeout=7)
        if info_res.status_code == 200:
            info = info_res.json()
            title = info.get('title', 'Anime')
            episodes = [ep['number'] for ep in info.get('episodes', [])]
            
            if episodes and current_ep <= len(episodes):
                target_ep_id = info['episodes'][current_ep - 1]['id']
                watch_res = requests.get(f"{BASE_API}/watch/{target_ep_id}", timeout=7)
                if watch_res.status_code == 200:
                    watch_data = watch_res.json()
                    if 'headers' in watch_data and 'Referer' in watch_data['headers']:
                        video_url = watch_data['headers']['Referer']
    except:
        pass

    return render_template_string(HTML_TEMPLATE, view='player', anime_id=anime_id, title=title, current_ep=current_ep, episodes=episodes, video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
