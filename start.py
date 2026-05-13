#!/usr/bin/env python3
"""
一键启动脚本 - 多模型运价预测系统
支持 Windows, macOS, Linux

使用方法:
  Windows:   python start.py
  macOS/Linux: python3 start.py
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# 彩色输出
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*40}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(40)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*40}{Colors.END}\n")

def print_info(icon, text):
    print(f"{icon} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_action(text):
    print(f"{Colors.MAGENTA}🚀 {text}{Colors.END}")

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# 确定系统类型
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"

def setup_backend():
    """设置后端环境"""
    print_action("设置后端环境...")
    
    # 虚拟环境路径
    if IS_WINDOWS:
        venv_python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
        pip_exe = BACKEND_DIR / ".venv" / "Scripts" / "pip.exe"
    else:
        venv_python = BACKEND_DIR / ".venv" / "bin" / "python"
        pip_exe = BACKEND_DIR / ".venv" / "bin" / "pip"
    
    # 创建虚拟环境
    if not (BACKEND_DIR / ".venv").exists():
        print_warning("虚拟环境不存在，正在创建...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=BACKEND_DIR, check=True)
        print_success("虚拟环境创建完成")
    else:
        print_success("虚拟环境已存在")
    
    # 安装依赖
    requirements_file = BACKEND_DIR / "requirements.txt"
    if requirements_file.exists():
        print_action("安装后端依赖...")
        subprocess.run([str(pip_exe), "install", "-q", "-r", str(requirements_file)], 
                      cwd=BACKEND_DIR, check=False)
        print_success("后端依赖已安装")
    
    # 数据库迁移
    print_action("执行数据库迁移...")
    subprocess.run([str(venv_python), "manage.py", "makemigrations", "--noinput"],
                  cwd=BACKEND_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([str(venv_python), "manage.py", "migrate", "--noinput"],
                  cwd=BACKEND_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print_success("数据库迁移完成")
    
    return str(venv_python)

def setup_frontend():
    """设置前端环境"""
    print_action("设置前端环境...")
    
    # 检查 node_modules
    if not (FRONTEND_DIR / "node_modules").exists():
        print_warning("依赖未安装，正在安装 npm 包...")
        subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
        print_success("npm 包已安装")
    else:
        print_success("npm 包已安装")

def start_backend(venv_python):
    """启动后端"""
    print_action("启动后端服务 (127.0.0.1:8001)...")
    
    if IS_WINDOWS:
        # Windows: 在新窗口中启动
        subprocess.Popen(
            f'cmd /k "{venv_python}" manage.py runserver 127.0.0.1:8001',
            cwd=BACKEND_DIR,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # macOS/Linux: 后台启动
        subprocess.Popen(
            [venv_python, "manage.py", "runserver", "127.0.0.1:8001"],
            cwd=BACKEND_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    print_success("后端已启动 (新窗口)")

def start_frontend():
    """启动前端"""
    print_action("启动前端服务 (http://localhost:5173)...")
    
    if IS_WINDOWS:
        # Windows: 在新窗口中启动
        subprocess.Popen(
            "cmd /k npm run dev",
            cwd=FRONTEND_DIR,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # macOS/Linux: 后台启动
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    print_success("前端已启动 (新窗口)")

def main():
    """主函数"""
    print("\n")
    print_header("多模型运价预测系统 - 一键启动")
    print_info("📁", f"项目根目录: {PROJECT_ROOT}")
    print_info("💻", f"系统: {SYSTEM}")
    print("\n")
    
    try:
        # 验证目录存在
        if not BACKEND_DIR.exists():
            print_error("后端目录不存在")
            sys.exit(1)
        if not FRONTEND_DIR.exists():
            print_error("前端目录不存在")
            sys.exit(1)
        
        # 设置后端
        print_action("🔧 设置后端环境...")
        venv_python = setup_backend()
        print("\n")
        
        # 设置前端
        print_action("🔧 设置前端环境...")
        setup_frontend()
        print("\n")
        
        # 启动服务
        print_header("启动服务")
        start_backend(venv_python)
        time.sleep(3)  # 等待后端启动
        start_frontend()
        
        print("\n")
        print_header("服务启动成功！")
        print_info("📍", "后端地址: http://127.0.0.1:8001")
        print_info("📍", "前端地址: http://localhost:5173")
        print("\n")
        print_info("💡", "提示: 两个新的窗口将打开，分别运行后端和前端")
        print_info("⏹️ ", "要停止服务，关闭这两个窗口或按 Ctrl+C")
        print("\n")
        
        # 主程序继续运行
        if not IS_WINDOWS:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n程序已停止")
                sys.exit(0)
    
    except FileNotFoundError as e:
        print_error(f"文件不存在: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
