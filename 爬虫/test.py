import json
import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config import client, KIMI_MODEL


def fetch_page(url: str) -> str:
    """抓取网页 HTML"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text


def find_result_urls(html: str, base_url: str) -> list[str]:
    """在页面中寻找可能与结果/排名相关的链接"""
    soup = BeautifulSoup(html, "html.parser")
    candidates: set[str] = set()

    keywords = ["result", "standing", "ranking", "scoreboard", "worldfinal", "world-finals"]

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = (a.get_text() or "").lower()
        href_lower = href.lower()

        if any(k in href_lower for k in keywords) or any(k in text for k in keywords):
            full_url = urljoin(base_url, href)
            candidates.add(full_url)

    return sorted(candidates)


def extract_icpc_rankings_with_kimi(html: str, url: str):
    """调用 Kimi，从 HTML 中提取 ICPC 历年排名信息，返回 JSON 列表"""
    prompt = f"""
你是一个网页信息抽取助手。

下面是网页 HTML 内容（来自 {url} ）：
---------------- HTML 开始 ----------------
{html[:40000]}
---------------- HTML 结束 ----------------

你的任务是从中抽取 **ICPC（International Collegiate Programming Contest）历年的比赛排名信息**。

请你：
1. 找出页面上与 ICPC 结果 / standings / results / rankings / world finals / regional contests 等相关的内容；
2. 尽可能提取「历年」或「多个年份」的信息；
3. 对每一条“比赛记录”输出以下字段：
   - year: 年份（整数，例如 2024）
   - contest_name: 比赛名称（例如 "ICPC World Finals 2024"）
   - rank: 名次（整数，如果是一个队伍的具体名次）
   - team_name: 队伍名称（字符串）
   - university: 学校名称（字符串，如果能从上下文推断）
   - region: 赛区/国家（如能推断则填写，否则用 null）
   - category: 比赛类别（例如 "World Finals", "Regional", "National"，不确定就用 null）
   - link: 与该比赛或结果相关的网页链接（相对链接请补全为绝对链接，如果没有就用 null）

4. 以 **JSON 数组** 的形式返回，类似：
[
  {{
    "year": 2024,
    "contest_name": "ICPC World Finals 2024",
    "rank": 1,
    "team_name": "Example Team",
    "university": "Example University",
    "region": "Asia",
    "category": "World Finals",
    "link": "https://icpc.global/.../results"
  }},
  ...
]

只返回合法 JSON，不要附带任何解释性文字或注释。
"""

    response = client.chat.completions.create(
        model=KIMI_MODEL,
        messages=[
            {"role": "system", "content": "你是一个擅长从 HTML 中抽取结构化信息的助手。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)


if __name__ == "__main__":
    # ICPC 官网首页
    base_url = "https://icpc.global/"
    print("正在抓取网页：", base_url)
    html = fetch_page(base_url)

    # 第一步：从首页寻找可能的“结果/排名”链接
    print("正在分析首页，查找结果/排名相关链接...")
    result_urls = find_result_urls(html, base_url)
    print(f"找到疑似结果页面 {len(result_urls)} 个：")
    for u in result_urls:
        print(" -", u)

    all_rankings: list[dict] = []

    # 第二步：对每个结果页面调用 Kimi 抽取排名
    for idx, url in enumerate(result_urls, start=1):
        try:
            print(f"\n[{idx}/{len(result_urls)}] 抓取结果页面：{url}")
            page_html = fetch_page(url)
            rankings = extract_icpc_rankings_with_kimi(page_html, url)

            if isinstance(rankings, list):
                all_rankings.extend(rankings)
                print(f"该页面抽取到 {len(rankings)} 条记录。")
            else:
                print("Kimi 返回的不是列表，已忽略。")
        except Exception as e:
            print(f"处理 {url} 时出错：{e}")

    print("\n汇总抽取结果：")
    print(f"总共抽取到 {len(all_rankings)} 条排名记录。")
    print(json.dumps(all_rankings, indent=4, ensure_ascii=False))

