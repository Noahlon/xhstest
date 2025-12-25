#!/usr/bin/env python3
import time
import urllib.parse
import openpyxl

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


# ====== 打开本地 Chrome（使用你提供的配置） ======
def open_chrome():
    options = Options()

    # macOS 本地 Chrome 路径
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    # 禁止“Chrome 正受到自动测试软件的控制”提示条
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    return driver


# ====== 逐行读取 Excel：返回 (第一列, 第二列) ======
def iter_excel_cols12(file_path: str, sheet_name: str = None):
    """
    逐行读取 Excel，每次返回 (第一列, 第二列)。
    如第一行是表头，把 min_row 改成 2。
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    for row in ws.iter_rows(min_row=1, values_only=True):
        col1 = row[0] if len(row) > 0 else None
        col2 = row[1] if len(row) > 1 else None
        yield col1, col2


# ====== 检测是否是验证码 / 异常流量页面，如是则暂停等待人工 ======
def wait_if_verification(driver):
    """
    简单检测是否处在 Google 的验证 / 异常流量页面。
    如果检测到，则提示你在浏览器中手动完成验证，然后按回车继续。
    """
    title = (driver.title or "").lower()
    url = (driver.current_url or "").lower()

    suspicious = False

    # 方法 1：标题和 URL 关键字
    if any(k in title for k in ["captcha", "unusual traffic", "verify"]) or \
       any(k in url for k in ["sorry", "unusualtraffic", "recaptcha"]):
        suspicious = True

    # 方法 2：尝试判断是否是正常搜索结果页
    #   正常搜索页一般会有 id="search" 的元素
    if not suspicious:
        try:
            driver.find_element(By.ID, "search")
        except NoSuchElementException:
            # 没找到搜索结果区域，也可能是验证页或错误页
            suspicious = True

    if suspicious:
        print("⚠️ 可能遇到 Google 验证 / 异常流量页面：")
        print("   标题:", driver.title)
        print("   URL  :", driver.current_url)
        input("👉 请在浏览器中手动完成验证或刷新，确认页面正常后，回到终端按回车继续...")
        return True

    return False


# ====== 通过 URL 新开标签页搜索 ======
def google_search_by_url_new_tab(driver, query: str):
    # URL 编码搜索词（中文、空格等）
    encoded_query = urllib.parse.quote_plus(query)  # 空格 -> +

    url = f"https://www.google.com/search?q={encoded_query}"

    # 新开标签页并切换
    driver.execute_script(f"window.open('{url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    # 等页面加载一会儿
    time.sleep(3)

    # 检测是否被验证码拦截，如果是则暂停等待人工处理
    wait_if_verification(driver)


def main():
    excel_path = "/Users/liuqianlong/Documents/code/xhscase/web_file_transfer/data/工作簿1.xlsx"  # 修改为你的 Excel 路径
    sheet_name = None

    driver = open_chrome()
    try:
        # 先打开 Google 主页（有时第一次就触发验证）
        driver.get("https://www.google.com")
        time.sleep(3)
        wait_if_verification(driver)
        i = 0
        for col1, col2 in iter_excel_cols12(excel_path, sheet_name):
            
            if not col1 and not col2:
                continue

            part1 = "" if col1 is None else str(col1)
            part2 = "" if col2 is None else str(col2)
            query = f"{part1} {part2} github".strip()
        
            if not query:
                continue

            print("正在新标签页搜索：", query)
            if i < 100:
                i += 1
                continue
            google_search_by_url_new_tab(driver, query)

            # 为了减少触发频率，适当暂停
            time.sleep(0.2)
            # 每搜索 10 次，暂停
            if (i + 1) % 10 == 0:
                input("✅ 已搜索 10 次，按回车继续...")
            i += 1

        input("✅ 所有搜索处理完毕。按回车关闭浏览器…")
    finally:
        print("关闭浏览器...")
        # driver.quit()


if __name__ == "__main__":
    main()
