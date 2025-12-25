import os
import csv
import time
import json
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
import pdfplumber
import docx

import autogen
from autogen import AssistantAgent, UserProxyAgent

import os

KEY = os.environ.get("KEY")
MODEL = os.environ.get("MODEL")
BASE_URL = os.environ.get("BASE_URL")  

#########################################
# 0. 基础配置
#########################################

# 如果用 OpenAI / DeepSeek 等云模型，在环境变量中设置：OPENAI_API_KEY / DEEPSEEK_API_KEY
# 如果用本地模型（如 Ollama），请按你的情况配置 config_list
# 下面是一个通用 config_list 示例（你需要根据实际情况修改）：

config_list = [
    {
        "model": MODEL,  # 或者 'gpt-4o', 'deepseek-chat', 本地模型等
        "api_key": KEY,
        "base_url": BASE_URL
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.2,
    "timeout": 120,
    # 控制成本和调用限制
    "max_tokens": 2048,
}


#########################################
# 1. 工具函数：GitHub 搜索 & 内容抓取
#########################################

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_CONTENTS_URL = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # 建议设置，提高 rate limit

def github_search_repos(query: str, per_page: int = 10) -> List[Dict[str, Any]]:
    """使用 GitHub 搜索 API 搜索仓库。"""
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    params = {
        "q": query,
        "per_page": per_page,
        "sort": "stars",
        "order": "desc"
    }
    resp = requests.get(GITHUB_SEARCH_URL, headers=headers, params=params)
    if resp.status_code != 200:
        print("GitHub search error:", resp.status_code, resp.text)
        return []
    data = resp.json()
    return data.get("items", [])


def github_list_repo_files(owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
    """列出指定仓库路径下的文件和目录（简单做法，不递归）。"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json()


def github_download_raw_file(owner: str, repo: str, branch: str, path: str) -> bytes:
    """下载仓库中的原始文件内容。"""
    url = GITHUB_RAW_URL.format(owner=owner, repo=repo, branch=branch, path=path)
    resp = requests.get(url)
    if resp.status_code != 200:
        return b""
    return resp.content


def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    """从 PDF 字节中提取文本。"""
    import io
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text


def parse_docx_bytes(docx_bytes: bytes) -> str:
    """从 docx 字节中提取文本。"""
    import io
    f = io.BytesIO(docx_bytes)
    document = docx.Document(f)
    text = []
    for para in document.paragraphs:
        text.append(para.text)
    return "\n".join(text)


#########################################
# 2. 定义 Agents
#########################################

# 2.1 User Proxy
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="你是任务发起者，负责和其他 Agents 协调，最终得到简历表格。",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},  # 关键配置
)

# 2.2 Planner Agent: 生成搜索策略
planner_agent = AssistantAgent(
    name="planner_agent",
    llm_config=llm_config,
    system_message=(
        "你是搜索规划 Agent。"
        "根据用户需求，生成适合 GitHub 搜索 API 的 query 列表，"
        "目标是找到复旦大学学生的个人简历仓库。"
        "返回 JSON 格式，只包含一个字段 'queries'，"
        "例如：{\"queries\":[\"query1\",\"query2\"]}。"
        "注意多用中英文关键词，如：Fudan University, 复旦大学, resume, CV, 简历, 个人简历；"
        "并使用 in:name, in:description, in:readme 等 GitHub 搜索语法。"
    ),
)

# 2.3 Search Agent: 调用 GitHub 搜索
class SearchAgent(AssistantAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        all_repos = []
        for q in queries:
            print(f"[SearchAgent] Searching GitHub with query: {q}")
            repos = github_search_repos(q, per_page=10)
            all_repos.extend(repos)
            time.sleep(1)  # 防止频率过高
        # 去重（基于 full_name）
        unique = {}
        for r in all_repos:
            unique[r["full_name"]] = r
        return list(unique.values())

search_agent = SearchAgent(
    name="search_agent",
    llm_config=None,  # 不需要 LLM
    system_message="你负责调用 GitHub 搜索工具函数。",
)

# 2.4 Filter Agent: 判断是否复旦学生 & 是否简历
filter_agent = AssistantAgent(
    name="filter_agent",
    llm_config=llm_config,
    system_message=(
        "你是筛选 Agent。"
        "输入是一组 GitHub 仓库的基本信息（JSON 列表），"
        "你需要判断哪些是“复旦大学学生的公开个人简历仓库”。"
        "判断依据可以包括：仓库名、描述、owner 名、是否包含 resume/cv 等词。"
        "输出严格为 JSON，字段：'selected_repos'，其值为原始列表中的子集。"
        "不要添加多余说明文字。"
    ),
)

# 2.5 Extract Agent: 在仓库中定位简历文件并解析内容
class ExtractAgent(AssistantAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def find_and_parse_resume(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        给定 GitHub repo（search API 返回的 item），
        尝试查找简历文件并解析出文本，然后让 LLM 抽取结构化字段。
        """
        owner = repo["owner"]["login"]
        name = repo["name"]
        default_branch = repo.get("default_branch", "main")

        # 1) 列出根目录文件
        contents = github_list_repo_files(owner, name, "")
        if not isinstance(contents, list):
            return {}

        candidate_files = []
        resume_keywords = ["resume", "cv", "curriculum", "简历", "个人简历"]
        exts = [".pdf", ".md", ".txt", ".docx"]

        for item in contents:
            if item.get("type") != "file":
                continue
            fname = item["name"].lower()
            if any(kw in fname for kw in resume_keywords) and any(
                fname.endswith(e) for e in exts
            ):
                candidate_files.append(item["path"])

        # 如果根目录没发现，就尝试 README 当简历
        readme_paths = [c["path"] for c in contents if c.get("name", "").lower().startswith("readme")]
        if not candidate_files:
            candidate_files.extend(readme_paths)

        if not candidate_files:
            return {}

        # 2) 只取第一个候选文件做示例（你可以扩展做多文件）
        resume_path = candidate_files[0]
        print(f"[ExtractAgent] Found candidate resume file: {owner}/{name}/{resume_path}")

        raw_bytes = github_download_raw_file(owner, name, default_branch, resume_path)
        if not raw_bytes:
            return {}

        text = ""
        rp_lower = resume_path.lower()
        try:
            if rp_lower.endswith(".pdf"):
                text = parse_pdf_bytes(raw_bytes)
            elif rp_lower.endswith(".docx"):
                text = parse_docx_bytes(raw_bytes)
            else:
                # md / txt 统一按 utf-8 尝试解码
                text = raw_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[ExtractAgent] parse error: {e}")
            return {}

        if not text.strip():
            return {}

        # 3) 调用 LLM 抽取结构化信息
        prompt = f"""
下面是一份可能的个人简历文本，请你提取关键信息，以 JSON 格式返回：

要求字段：
- name: 姓名
- university: 学校
- degree: 学位或年级（如本科/硕士/博士）
- major: 专业
- graduation_year: 毕业年份（如果有）
- skills: 技能列表（编程语言、技术栈等）
- github_url: GitHub 主页链接（如果有）
- email: 邮箱（如果有）

只返回 JSON，不要其他解释。

简历内容：
{text}
"""

        resp = self.generate_reply(messages=[{"role": "user", "content": prompt}])
        # 尝试从回复中解析 JSON
        try:
            # 如果回复中包含 markdown ```json 包裹，先去掉
            content = resp["content"] if isinstance(resp, dict) else resp
            if "```" in content:
                content = content.split("```")[1]
                if content.strip().lower().startswith("json"):
                    content = "\n".join(content.split("\n")[1:])
            data = json.loads(content)
        except Exception:
            data = {}

        result = {
            "repo_full_name": repo["full_name"],
            "repo_html_url": repo["html_url"],
            "resume_path": resume_path,
            "resume_raw_url": GITHUB_RAW_URL.format(
                owner=owner, repo=name, branch=default_branch, path=resume_path
            ),
            "llm_extract": data,
        }
        return result


extract_agent = ExtractAgent(
    name="extract_agent",
    llm_config=llm_config,
    system_message="你负责从简历文本中抽取结构化信息。",
)


# 2.6 CSV Agent: 把结果写入 CSV
class CSVAgent(AssistantAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write_csv(self, records: List[Dict[str, Any]], filename: str = "fudan_github_resumes.csv"):
        fieldnames = [
            "name",
            "university",
            "degree",
            "major",
            "graduation_year",
            "skills",
            "email",
            "github_url",
            "repo_full_name",
            "repo_html_url",
            "resume_path",
            "resume_raw_url",
        ]
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                llm = r.get("llm_extract", {}) or {}
                writer.writerow(
                    {
                        "name": llm.get("name", ""),
                        "university": llm.get("university", ""),
                        "degree": llm.get("degree", ""),
                        "major": llm.get("major", ""),
                        "graduation_year": llm.get("graduation_year", ""),
                        "skills": ", ".join(llm.get("skills", [])) if isinstance(llm.get("skills"), list) else llm.get("skills", ""),
                        "email": llm.get("email", ""),
                        "github_url": llm.get("github_url", ""),
                        "repo_full_name": r.get("repo_full_name", ""),
                        "repo_html_url": r.get("repo_html_url", ""),
                        "resume_path": r.get("resume_path", ""),
                        "resume_raw_url": r.get("resume_raw_url", ""),
                    }
                )
        print(f"[CSVAgent] 写入 CSV 完成：{filename}")


csv_agent = CSVAgent(
    name="csv_agent",
    llm_config=None,
    system_message="你负责把结构化数据写入 CSV 文件。",
)


#########################################
# 3. 主流程：多 Agent 编排
#########################################

def main():
    # Step 1: Planner 生成 GitHub 搜索 query
    task_desc = (
        "帮我生成多组 GitHub 搜索 query，目标是找到“复旦大学学生在 GitHub 公开的个人简历仓库”。"
        "只返回 JSON，例如：{\"queries\":[\"query1\",\"query2\"]}。"
    )
    planner_reply = planner_agent.generate_reply(messages=[{"role": "user", "content": task_desc}])
    planner_content = planner_reply["content"] if isinstance(planner_reply, dict) else planner_reply
    print("[PlannerAgent] reply:", planner_content)

    # 解析 JSON
    try:
        if "```" in planner_content:
            part = planner_content.split("```")[1]
            if part.strip().lower().startswith("json"):
                part = "\n".join(part.split("\n")[1:])
            planner_data = json.loads(part)
        else:
            planner_data = json.loads(planner_content)
    except Exception as e:
        print("解析 planner 回复失败：", e)
        return

    queries = planner_data.get("queries", [])
    if not queries:
        print("没有生成有效的 queries。")
        return

    # Step 2: SearchAgent 用这些 query 搜仓库
    repos = search_agent.search(queries)
    print(f"[SearchAgent] total repos found: {len(repos)}")

    if not repos:
        print("GitHub 搜索没有结果。")
        return

    # Step 3: FilterAgent 过滤，保留“复旦学生简历仓库”
    filter_input = json.dumps(repos, ensure_ascii=False)
    filter_prompt = f"下面是 GitHub 搜索到的仓库列表（JSON）：\n{filter_input}\n\n请按系统提示筛选，并输出结果。"
    filter_reply = filter_agent.generate_reply(messages=[{"role": "user", "content": filter_prompt}])
    filter_content = filter_reply["content"] if isinstance(filter_reply, dict) else filter_reply
    print("[FilterAgent] reply:", filter_content)

    try:
        if "```" in filter_content:
            part = filter_content.split("```")[1]
            if part.strip().lower().startswith("json"):
                part = "\n".join(part.split("\n")[1:])
            filter_data = json.loads(part)
        else:
            filter_data = json.loads(filter_content)
    except Exception as e:
        print("解析 filter 回复失败：", e)
        return

    selected_repos = filter_data.get("selected_repos", [])
    print(f"[FilterAgent] selected repos: {len(selected_repos)}")

    if not selected_repos:
        print("没有被判断为复旦学生简历的仓库。")
        return

    # Step 4: ExtractAgent 逐个仓库解析简历内容并抽取信息
    records = []
    for repo in selected_repos:
        try:
            res = extract_agent.find_and_parse_resume(repo)
            if res:
                records.append(res)
        except Exception as e:
            print(f"[ExtractAgent] error on repo {repo.get('full_name')}: {e}")
        time.sleep(1)

    if not records:
        print("未从候选仓库中成功解析出简历。")
        return

    # Step 5: CSVAgent 写入 CSV
    csv_agent.write_csv(records)


if __name__ == "__main__":
    main()
