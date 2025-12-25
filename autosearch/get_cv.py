import time
import json
import requests

GITHUB_API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    # 建议配置自己的 GitHub token，提高 API 限额：
    # "Authorization": "Bearer YOUR_GITHUB_TOKEN",
    "User-Agent": "sjtu-resume-crawler-demo"
}

# 判断“可能是上海交通大学”的关键词
SJTU_KEYWORDS = [
    "上海交通大学",
    "shanghai jiao tong university",
    "shanghai jiaotong university",
    "shanghai jiao-tong university",
    "sjtu"
]

# 判断“可能是简历”的关键词
RESUME_KEYWORDS = [
    "resume",
    "curriculum vitae",
    "cv",
    "简历",
    "个人简历",
    "教育经历",
    "工作经历",
    "项目经验"
]

def looks_like_sjtu_user(user: dict) -> bool:
    """
    根据 bio / location / company 粗略判断是否可能是上海交通大学相关用户
    """
    text_fields = []
    for key in ("bio", "location", "company"):
        v = user.get(key)
        if isinstance(v, str):
            text_fields.append(v.lower())

    if not text_fields:
        return False

    joined = " ".join(text_fields)
    for kw in SJTU_KEYWORDS:
        if kw.lower() in joined:
            return True
    return False

def looks_like_resume(html: str) -> bool:
    lower_html = html.lower()
    return any(kw.lower() in lower_html for kw in RESUME_KEYWORDS)

def get_users_since(since: int, per_page: int = 100):
    """
    从 GitHub API 分页获取用户列表
    https://api.github.com/users?since=...
    """
    url = f"{GITHUB_API}/users"
    params = {"since": since, "per_page": per_page}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        print(f"[WARN] 获取用户失败 since={since}, status={resp.status_code}")
        return []
    return resp.json()

def fetch_github_io(username: str):
    """
    访问 username.github.io 首页
    """
    url = f"https://{username}.github.io/"
    try:
        resp = requests.get(url, headers={"User-Agent": "sjtu-resume-crawler-demo"}, timeout=10)
        if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
            return resp.text
    except requests.RequestException as e:
        print(f"[WARN] 访问 {url} 出错：{e}")
    return None

def main():
    since = 0          # 从哪个 GitHub user id 开始
    max_rounds = 50    # 扫多少批用户，可根据需要调大
    sjtu_users = []    # 疑似上交大用户列表
    sjtu_resumes = []  # 疑似上交大简历列表

    for round_idx in range(max_rounds):
        print(f"=== Round {round_idx + 1}/{max_rounds}, since={since} ===")
        users = get_users_since(since, per_page=100)
        if not users:
            break

        for user in users:
            username = user.get("login")
            if not username:
                continue

            # 筛选是否像上交大用户
            if not looks_like_sjtu_user(user):
                continue

            print(f"[SJTU?] {username} (id={user.get('id')}), checking github.io ...")
            sjtu_users.append(user)

            # 检查 GitHub Pages
            html = fetch_github_io(username)
            time.sleep(1)  # 礼貌延时，避免对 GitHub Pages 造成压力

            if not html:
                continue

            if looks_like_resume(html):
                url = f"https://{username}.github.io/"
                print(f"[RESUME FOUND] {url}")
                sjtu_resumes.append({
                    "username": username,
                    "id": user.get("id"),
                    "url": url
                })

        since = users[-1]["id"]
        time.sleep(5)  # 避免频繁调用 GitHub API

    # 保存结果
    with open("sjtu_users.json", "w", encoding="utf-8") as f:
        json.dump(sjtu_users, f, ensure_ascii=False, indent=2)
    with open("sjtu_resumes.json", "w", encoding="utf-8") as f:
        json.dump(sjtu_resumes, f, ensure_ascii=False, indent=2)

    print(f"疑似上海交通大学用户数：{len(sjtu_users)}")
    print(f"其中疑似简历页面数：{len(sjtu_resumes)}，保存在 sjtu_resumes.json")

if __name__ == "__main__":
    main()
