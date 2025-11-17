#!/usr/bin/env python3
import cgi
import os
import sys
from datetime import datetime

# 设置编码
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 创建基础上传目录
BASE_UPLOAD_DIR = 'uploads'
if not os.path.exists(BASE_UPLOAD_DIR):
    os.makedirs(BASE_UPLOAD_DIR)

def get_today_upload_dir():
    """获取今天的上传目录路径，如果不存在则创建"""
    today_str = datetime.now().strftime("%Y%m%d")
    today_dir = os.path.join(BASE_UPLOAD_DIR, today_str)
    
    if not os.path.exists(today_dir):
        os.makedirs(today_dir)
    
    return today_dir

def save_uploaded_file():
    """处理文件上传"""
    try:
        # 解析multipart/form-data
        form = cgi.FieldStorage()
        
        # 检查是否有文件
        if 'file' not in form:
            print("Status: 400 Bad Request")
            print("Content-Type: text/plain; charset=utf-8")
            print()
            print("错误：没有接收到文件")
            return
        
        fileitem = form['file']
        
        # 检查是否是文件
        if not fileitem.file:
            print("Status: 400 Bad Request")
            print("Content-Type: text/plain; charset=utf-8")
            print()
            print("错误：无效的文件")
            return
        
        # 获取原始文件名
        if fileitem.filename:
            original_filename = fileitem.filename
            # 安全处理文件名
            safe_filename = os.path.basename(original_filename)
        else:
            print("Status: 400 Bad Request")
            print("Content-Type: text/plain; charset=utf-8")
            print()
            print("错误：无效的文件名")
            return
        
        # 获取今天的上传目录
        upload_dir = get_today_upload_dir()
        
        # 生成带时间戳的新文件名，避免冲突
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{timestamp}_{safe_filename}"
        # filename = f"{safe_filename}_{timestamp}"
        filepath = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(filepath, 'wb') as f:
            while True:
                chunk = fileitem.file.read(8192)  # 8KB chunks
                if not chunk:
                    break
                f.write(chunk)
        
        # 返回成功响应，包含日期目录信息
        date_dir = os.path.basename(upload_dir)
        print("Status: 200 OK")
        print("Content-Type: application/json; charset=utf-8")
        print()
        print(f'{{"status": "success", "filename": "{filename}", "date_dir": "{date_dir}", "message": "文件上传成功"}}')
        
    except Exception as e:
        print("Status: 500 Internal Server Error")
        print("Content-Type: application/json; charset=utf-8")
        print()
        print(f'{{"status": "error", "message": "服务器错误: {str(e)}"}}')

if __name__ == '__main__':
    save_uploaded_file()