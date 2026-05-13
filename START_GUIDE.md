# 🚀 一键启动说明

本项目提供了 **3 种启动方式**，选择最适合你的方式运行。

---

## 📋 方案对比

| 方案 | 文件 | 系统 | 使用方式 | 难度 |
|------|------|------|---------|------|
| **方案 1** | `start.ps1` | Windows | PowerShell 运行 | ⭐⭐ |
| **方案 2** | `start.bat` | Windows | 双击运行 | ⭐ |
| **方案 3** | `start.py` | 全部 | Python 运行 | ⭐⭐ |

---

## 方案 1️⃣ : PowerShell 脚本 (推荐 Windows)

### 使用步骤

1. **打开 PowerShell**
   - 在项目根目录按 `Shift + 右键` → 选择"在此处打开 PowerShell"
   - 或直接在任务栏搜索 "PowerShell"

2. **运行脚本**
   ```powershell
   .\start.ps1
   ```

3. **如果遇到权限错误**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   然后重新运行脚本

### 功能
✅ 自动创建虚拟环境  
✅ 自动安装依赖  
✅ 自动执行数据库迁移  
✅ 在新窗口中同时启动后端和前端  
✅ 彩色输出提示  

---

## 方案 2️⃣ : Batch 脚本 (最简单)

### 使用步骤

1. **双击运行**
   - 在文件管理器中找到 `start.bat`
   - 双击即可运行

2. **或者用命令运行**
   ```cmd
   start.bat
   ```

### 功能
✅ 无需配置执行策略  
✅ 最简单的启动方式  
✅ 自动配置环境和依赖  
✅ 在新窗口中启动服务  

---

## 方案 3️⃣ : Python 脚本 (跨平台)

### 使用步骤

#### Windows
```cmd
python start.py
```

#### macOS / Linux
```bash
python3 start.py
```

### 功能
✅ 支持 Windows / macOS / Linux  
✅ 自动检测系统环境  
✅ 丰富的彩色输出和进度提示  
✅ 完整的错误处理  

---

## 🔧 启动脚本做了什么？

```
1️⃣ 检查并创建虚拟环境
   └─ 若不存在，自动创建 .venv

2️⃣ 激活虚拟环境
   └─ 加载 Python 环境

3️⃣ 安装/更新依赖
   └─ pip install -r requirements.txt

4️⃣ 执行数据库迁移
   └─ makemigrations + migrate

5️⃣ 安装前端依赖
   └─ npm install (若需要)

6️⃣ 启动后端服务
   └─ Django runserver (127.0.0.1:8001)
   └─ 在新窗口打开

7️⃣ 启动前端服务
   └─ npm run dev (http://localhost:5173)
   └─ 在新窗口打开

✅ 完成！
```

---

## 📱 访问应用

启动完成后，自动打开两个新窗口：

| 服务 | 地址 | 说明 |
|------|------|------|
| **后端** | http://127.0.0.1:8001 | Django API 服务 |
| **前端** | http://localhost:5173 | Vue3 应用界面 |

在浏览器中打开 **http://localhost:5173** 即可使用应用。

---

## 🛑 停止服务

### 方式 1: 关闭窗口
- 点击两个启动的新窗口的关闭按钮

### 方式 2: 按 Ctrl+C
- 在任一启动窗口中按 `Ctrl+C` 停止服务

### 方式 3: 强制停止
```powershell
# PowerShell
Stop-Process -Name python -Force
Stop-Process -Name node -Force
```

---

## ⚠️ 常见问题

### Q: 运行脚本提示"找不到 python"？
**A**: 确保 Python 已安装并添加到系统 PATH。
```cmd
python --version
```

### Q: 提示"npm: 无法识别的命令"？
**A**: 确保 Node.js 已安装。
```cmd
npm --version
```

### Q: 虚拟环境已存在但仍然安装失败？
**A**: 手动删除虚拟环境后重试：
```powershell
Remove-Item -Path "backend\.venv" -Recurse -Force
```

### Q: 前端编译缓存问题导致启动失败？
**A**: 清理缓存：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Q: 后端数据库被锁定（database is locked）？
**A**: 删除数据库并重建：
```cmd
cd backend
del db.sqlite3
python manage.py migrate
```

### Q: 两个启动窗口没有出现？
**A**: 使用 Python 脚本或 Batch 脚本替代，它们更可靠。

---

## 📝 手动启动方式（备选）

如果脚本不工作，可以手动启动：

### 手动启动后端
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

### 手动启动前端（新窗口）
```cmd
cd frontend
npm install
npm run dev
```

---

## 🎯 推荐使用顺序

### 首次使用（完整流程）
1. 使用 `start.bat` 或 `start.ps1`
2. 脚本会自动完成所有配置
3. 直接在浏览器中打开 http://localhost:5173

### 后续使用
- 直接运行 `start.bat` / `start.ps1` / `start.py`
- 无需手动操作

---

## 💡 提示

- 首次运行会比较慢（需要安装依赖），后续会快速启动
- 保持两个启动的窗口打开，直到完成工作
- 修改代码后，前端会自动热更新，后端需要手动重启

---

**祝你使用愉快！** 🎉
