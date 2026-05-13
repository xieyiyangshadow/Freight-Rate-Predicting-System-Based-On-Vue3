# 基于Vue3的多模型运价预测系统 - 详细项目文档

## 目录
1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [完整项目结构](#完整项目结构)
4. [数据库设计](#数据库设计)
5. [后端API接口](#后端api接口)
6. [前端页面功能](#前端页面功能)
7. [核心业务流程](#核心业务流程)
8. [任务队列系统](#任务队列系统)
9. [文件存储结构](#文件存储结构)
10. [配置和部署](#配置和部署)
11. [常见问题](#常见问题)

---

## 项目概述

### 系统定位
这是一个基于 Django + Vue3 的多模型运价预测系统，支持用户上传自定义 ML 模型、管理数据集、进行多模型运价预测、查看历史预测结果。

### 核心功能
- **用户管理**：注册、登录、登出（基于电话号码唯一标识）
- **数据集管理**：上传 CSV 数据集、查看数据内容、选择 target 列
- **模型管理**：上传预测模型、训练、查看模型性能指标
- **运价预测**：使用已训练的模型进行多模型联合预测
- **历史管理**：查看预测历史、过滤、导出结果、删除任务
- **异步任务处理**：使用内置后台队列处理模型训练和预测

### 技术栈
- **后端**：Django 5.2.7 + Django REST Framework + SQLite
- **前端**：Vue 3 + Vite + Element Plus + Axios
- **任务队列**：内置多线程后台工作队列（可升级到 Celery）
- **部署**：开发环境本地运行，生产环境可使用 Gunicorn + Nginx

---

## 系统架构

### 整体架构
```
┌─────────────────────────────────┐
│   前端层 (Vue3 + Element Plus)   │
│  Dashboard │ Models │ Datasets   │
│  Predict │ History               │
└──────────────┬──────────────────┘
         HTTP/AJAX
         ↓
┌─────────────────────────────────┐
│   后端层 (Django REST API)       │
│  Users │ MLModels │ Predictions  │
│  Datasets (新增)                │
└──────────────┬──────────────────┘
    ORM + task_queue
    ↓
┌─────────────────────────────────┐
│   存储层                        │
│  SQLite 数据库 + 文件系统       │
└─────────────────────────────────┘
```

---

## 完整项目结构

### 目录树
```
Freight-Rate-Predicting-System/
├── README.md
├── PROJECT_DOCS.md                  # 本文档
├── backend/
│   ├── manage.py                    # Django 管理脚本
│   ├── db.sqlite3                   # SQLite 数据库
│   ├── requirements.txt             # Python 依赖列表
│   ├── freight/                     # Django 项目配置包
│   │   ├── __init__.py
│   │   ├── settings.py              # 项目配置（数据库、Apps、中间件等）
│   │   ├── urls.py                  # 路由总入口
│   │   ├── wsgi.py                  # WSGI 配置
│   │   ├── task_queue.py            # ✨ 后台异步任务队列
│   │   └── request_utils.py         # 用户提取工具函数
│   ├── users/                       # 用户 App
│   │   ├── migrations/
│   │   ├── models.py                # User 模型（电话唯一）
│   │   ├── views.py                 # RegisterView, LoginView
│   │   ├── serializers.py           # 用户序列化器
│   │   ├── urls.py                  # /api/users/* 路由
│   │   └── admin.py
│   ├── mlmodels/                    # 模型管理 App
│   │   ├── migrations/
│   │   ├── models.py                # MLModel, Dataset 模型
│   │   ├── views.py                 # 模型和数据集视图
│   │   ├── serializers.py           # 模型和数据集序列化器
│   │   ├── urls.py                  # /api/models/* 路由
│   │   └── admin.py
│   ├── predictions/                 # 预测 App
│   │   ├── migrations/
│   │   ├── models.py                # PredictionTask 模型
│   │   ├── views.py                 # 预测任务视图
│   │   ├── serializers.py           # 任务序列化器
│   │   ├── urls.py                  # /api/predictions/* 路由
│   │   └── admin.py
│   ├── models_storage/              # 模型文件存储（自动创建）
│   ├── datasets_storage/            # ✨ 数据集存储（自动创建）
│   └── predictions_storage/         # 预测结果存储（自动创建）
├── frontend/
│   ├── package.json                 # npm 依赖与脚本
│   ├── index.html                   # HTML 入口
│   ├── vite.config.js               # Vite 配置（代理、插件）
│   ├── src/
│   │   ├── main.js                  # Vue 应用入口
│   │   ├── App.vue                  # 根组件（布局、路由）
│   │   ├── api.js                   # Axios 实例 + API 函数
│   │   ├── router.js                # Vue Router 配置
│   │   ├── styles/
│   │   │   └── global.css           # 全局样式（主题、栅格等）
│   │   └── pages/
│   │       ├── Login.vue            # 登录页
│   │       ├── Register.vue         # 注册页
│   │       ├── Dashboard.vue        # 仪表板
│   │       ├── Models.vue           # 模型管理
│   │       ├── Datasets.vue         # ✨ 数据集管理（新增）
│   │       ├── Predict.vue          # 预测任务创建
│   │       └── History.vue          # 历史任务查看
│   └── node_modules/                # npm 包（gitignore）
└── .git/                            # Git 版本控制
```

### 文件说明详表

| 文件 | 作用 | 关键代码 |
|------|------|---------|
| `backend/freight/settings.py` | Django 配置 | INSTALLED_APPS、DATABASES、REST_FRAMEWORK |
| `backend/freight/task_queue.py` | 任务队列系统 | enqueue_training(), enqueue_prediction(), worker loop |
| `backend/users/models.py` | 用户模型 | User extends AbstractUser with phone |
| `backend/mlmodels/models.py` | 模型和数据集 | MLModel with dataset FK, Dataset with columns |
| `backend/mlmodels/views.py` | 模型数据集视图 | DatasetListCreateView, DatasetDetailView with preview |
| `backend/predictions/models.py` | 预测任务模型 | PredictionTask with M2M models_used |
| `frontend/src/api.js` | API 客户端 | axios instance, API functions, auth header |
| `frontend/src/pages/Datasets.vue` | 数据集界面 | 上传、列表、详情、target 选择 |

---

## 数据库设计

### ER 图（简化表示）

```
users_user
  ├── id (PK)
  ├── phone (UNIQUE)
  └── username
       ↓ 1:N
mlmodels_dataset
  ├── id (PK)
  ├── owner_id (FK → users_user)
  └── target_column
       ↓ 1:N
mlmodels_mlmodel
  ├── id (PK)
  ├── owner_id (FK → users_user)
  ├── dataset_id (FK → mlmodels_dataset)
  └── status
       ↓ M:N
predictions_predictiontask
  ├── id (PK)
  ├── owner_id (FK → users_user)
  ├── models_used (M2M)
  └── status
```

### 完整表结构

#### 1. users_user 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 主键，自动递增 |
| username | VARCHAR(150) | UNIQUE | 用户名 |
| phone | VARCHAR(11) | UNIQUE | 电话号码，登录标识符 |
| password | VARCHAR(128) | - | 密码哈希 |
| email | VARCHAR(254) | - | 邮箱 |
| first_name | VARCHAR(150) | - | 名字 |
| last_name | VARCHAR(150) | - | 姓氏 |
| is_active | BOOLEAN | - | 是否激活 |
| date_joined | DATETIME | - | 注册时间 |

#### 2. mlmodels_dataset 表（新增）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 主键 |
| owner_id | INTEGER | FK | 所有者（users_user.id） |
| name | VARCHAR(200) | - | 数据集名称 |
| file_path | VARCHAR(500) | - | CSV 文件路径 |
| columns | TEXT | - | 列名 JSON 数组 |
| target_column | VARCHAR(200) | NULL | 目标列（可编辑） |
| uploaded_at | DATETIME | - | 上传时间 |

**columns 存储示例**:
```json
["distance", "weight", "price"]
```

#### 3. mlmodels_mlmodel 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 主键 |
| owner_id | INTEGER | FK | 所有者（users_user.id） |
| name | VARCHAR(200) | - | 模型名称 |
| file_path | VARCHAR(500) | - | 模型 pickle 文件路径 |
| metrics_path | VARCHAR(500) | - | 评估指标文件路径 |
| status | VARCHAR(20) | - | 状态: uploading/training/completed/failed |
| dataset_id | INTEGER | FK | 关联数据集（mlmodels_dataset.id）✨ |
| target_column | VARCHAR(200) | - | 目标列（从数据集复制）✨ |
| training_time | FLOAT | - | 训练耗时（秒） |
| created_at | DATETIME | - | 创建时间 |
| trained_at | DATETIME | - | 完成时间 |

#### 4. predictions_predictiontask 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 主键 |
| owner_id | INTEGER | FK | 创建者（users_user.id） |
| name | VARCHAR(200) | - | 任务名称 |
| origin | VARCHAR(100) | - | 出发地 |
| destination | VARCHAR(100) | - | 目标地 |
| status | VARCHAR(20) | - | 状态: running/completed/failed |
| output_folder | VARCHAR(500) | - | 输出文件夹路径 |
| created_at | DATETIME | - | 创建时间 |
| completed_at | DATETIME | NULL | 完成时间 |

#### 5. predictions_predictiontask_models_used 表（M2M 中间表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | PK |
| predictiontask_id | FK | 任务 ID |
| mlmodel_id | FK | 模型 ID |

---

## 后端 API 接口

### 基础信息
- **基础 URL**：`http://127.0.0.1:8001/api`
- **认证方式**：X-Client-User 请求头 + Django Session
- **返回格式**：JSON
- **开发代理**：Vite 配置将 `/api` 转发到后端

### 数据集接口（新增）

#### 1. 上传数据集
```
POST /api/models/datasets/
Content-Type: multipart/form-data
X-Client-User: 1

请求体:
  name: "北京-上海运价数据"
  file: <CSV 文件>
  target_column: "price"  # 可选，默认 NULL
```

**成功响应 (201)**:
```json
{
  "id": 1,
  "owner": 1,
  "name": "北京-上海运价数据",
  "file_path": "datasets_storage/1/dataset.csv",
  "columns": "[\"distance\", \"weight\", \"price\"]",
  "target_column": "price",
  "uploaded_at": "2026-05-09T10:00:00Z"
}
```

**错误响应 (400)**:
```json
{
  "name": ["This field may not be blank."],
  "file": ["No file was submitted."]
}
```

#### 2. 获取数据集列表
```
GET /api/models/datasets/?search=北京&ordering=-uploaded_at
X-Client-User: 1
```

**响应 (200)**:
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "北京-上海运价数据",
      "columns": "[\"distance\", \"weight\", \"price\"]",
      "target_column": "price",
      "uploaded_at": "2026-05-09T10:00:00Z"
    }
  ]
}
```

#### 3. 获取数据集详情（含预览）
```
GET /api/models/datasets/1/
X-Client-User: 1
```

**响应 (200)**:
```json
{
  "id": 1,
  "name": "北京-上海运价数据",
  "columns_list": ["distance", "weight", "price"],
  "target_column": "price",
  "total_rows": 1000,
  "data_preview": [
    {
      "distance": "100",
      "weight": "50",
      "price": "1050"
    },
    {
      "distance": "200",
      "weight": "75",
      "price": "1600"
    }
  ]
}
```

**关键实现**:
- `columns_list`：从 JSON 列解析后的列表
- `total_rows`：CSV 行数（不含header）
- `data_preview`：DictReader 读取的前 10 行

#### 4. 更新目标列
```
PATCH /api/models/datasets/1/
X-Client-User: 1
Content-Type: application/json

{
  "target_column": "weight"
}
```

**响应 (200)**:
```json
{
  "id": 1,
  "target_column": "weight"
}
```

### 用户接口

#### 注册
```
POST /api/users/register/
{
  "username": "user1",
  "phone": "13800138000",
  "password": "Password123"
}
```

**成功响应**:
```json
{
  "id": 1,
  "username": "user1",
  "phone": "13800138000"
}
```

#### 登录
```
POST /api/users/login/
{
  "phone": "13800138000",
  "password": "Password123"
}
```

### 模型接口

#### 上传模型
```
POST /api/models/
X-Client-User: 1
Content-Type: multipart/form-data

name: "预测模型v1"
file: <模型文件>
dataset: 1              # ✨ 数据集 ID
target_column: "price"  # ✨ 目标列
```

#### 获取模型详情
```
GET /api/models/1/
X-Client-User: 1
```

**响应**:
```json
{
  "id": 1,
  "name": "预测模型v1",
  "status": "completed",
  "dataset": 1,
  "target_column": "price",
  "metrics_text": "Accuracy: 0.95\nPrecision: 0.93",
  "training_time": 300.5
}
```

### 预测接口

#### 创建预测任务
```
POST /api/predictions/
X-Client-User: 1
{
  "name": "北京至上海预测",
  "origin": "北京",
  "destination": "上海",
  "models_used": [1, 2, 3]
}
```

**响应 (201)**:
```json
{
  "id": 1,
  "status": "running",
  "origin": "北京",
  "destination": "上海"
}
```

#### 获取任务详情
```
GET /api/predictions/1/
X-Client-User: 1
```

**响应**:
```json
{
  "id": 1,
  "status": "completed",
  "result_json": {
    "summary": {
      "baseline_price": 1000,
      "best_prediction": 1050,
      "avg_prediction": 1033
    },
    "models": [
      {
        "id": 1,
        "name": "模型A",
        "prediction": 1050,
        "confidence": 0.92
      }
    ]
  }
}
```

---

## 前端页面功能

### 1. Datasets 页面（新增功能）

**位置**: `frontend/src/pages/Datasets.vue`

#### 页面分布
- **顶部统计**：数据集总数、总行数、target 列统计
- **数据集列表**：表格展示名称、列数、target 列、上传时间
- **上传面板**：右侧抽屉，输入名称、选择文件、选择 target 列
- **详情抽屉**：查看、编辑 target 列、预览数据

#### 核心功能
1. **CSV 文件解析**
   - 用户选择文件后，前端用 FileReader 读取
   - 获取首行作为列名
   - 自动填充列名下拉框

2. **数据集上传**
   - FormData 包含 name, file, target_column
   - 调用 `uploadDataset()` API
   - 上传成功后刷新列表

3. **详情查看**
   - 点击"详情"打开抽屉
   - 显示基本信息、行数统计
   - 显示列名标签（target 列绿色突出）
   - 显示前 10 行数据预览表格

4. **Target 列修改**
   - 详情抽屉中下拉框选择 target 列
   - 点击"保存"调用 `updateDataset(id, {target_column})`
   - 成功后更新显示

### 2. Models 页面（已增强）

**位置**: `frontend/src/pages/Models.vue`

**增强内容**:
- 上传模型时可关联数据集
- 从数据集中自动选择 target 列
- 详情显示关联数据集和 target 列

### 3. Predict 页面

**位置**: `frontend/src/pages/Predict.vue`

**逻辑**:
- 用户选择多个模型创建预测任务
- ✨ 前端检查所有模型的 target_column 是否一致
- 不一致时弹出确认对话框
- 用户确认后创建任务

### 4. History 页面（已增强）

**位置**: `frontend/src/pages/History.vue`

**增强内容**:
- 列表显示模型 target 列
- 详情显示预测使用的模型和 target 列

---

## 核心业务流程

### 流程 1：数据集上传与管理

```
┌────────────────────────────────────────────────────┐
│ 用户进入 Datasets 页面                              │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ 点击"上传"按钮 → 抽屉打开                            │
│ - 输入数据集名称                                   │
│ - 选择 CSV 文件                                    │
│   (前端 FileReader 解析首行 → 填充列名下拉框)      │
│ - 从列名中选择 target 列                           │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ POST /api/models/datasets/                         │
│ FormData: {name, file, target_column}             │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ 后端处理：                                         │
│ 1. 创建 Dataset 记录                              │
│ 2. 保存 CSV 文件到 datasets_storage/{id}/        │
│ 3. 读取首行解析列名，存入 columns JSON             │
│ 4. 返回数据集信息                                 │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ 前端显示：                                         │
│ 1. "上传成功"提示                                  │
│ 2. 列表刷新，新数据集出现                          │
│ 3. 抽屉关闭                                        │
└────────────────────────────────────────────────────┘
```

### 流程 2：模型训练

```
用户上传模型
  ├─ 选择关联数据集 Dataset
  ├─ 系统自动填充 target_column
  └─ POST /api/models/
      ↓
后端创建 MLModel 记录，状态 = 'uploading'
立即返回 201 响应
      ↓
后台队列 (task_queue.py)
  ├─ _process_training() 取任务
  ├─ 加载数据集的 CSV 文件
  ├─ 训练模型（demo 中随机生成指标）
  ├─ 保存 model.pkl 到 models_storage/{id}/
  ├─ 生成 metrics.txt（accuracy, precision 等）
  └─ 更新 MLModel.status = 'completed'
      ↓
前端轮询 GET /api/models/{id}/
  └─ 检测 status 变为 'completed'，刷新详情
```

### 流程 3：多模型预测

```
用户创建预测任务
  ├─ 输入出发地、目标地
  ├─ 选择 3 个已完成的模型
  └─ POST /api/predictions/
      ↓
前端检查
  └─ 所有模型 target_column 是否一致
     (不一致 → 弹出确认对话框)
      ↓
后端创建 PredictionTask，状态 = 'running'
立即返回 201 响应
      ↓
后台队列 (task_queue.py)
  ├─ _process_prediction() 取任务
  ├─ 遍历 models_used 中的模型
  ├─ 对每个模型进行预测（demo 中随机生成）
  ├─ 整合预测结果生成 result.json
  ├─ 保存到 predictions_storage/{id}/result.json
  └─ 更新 PredictionTask.status = 'completed'
      ↓
前端轮询直到任务完成
  └─ 自动跳转到 History 页面展示结果
```

---

## 任务队列系统

### 文件位置
`backend/freight/task_queue.py`

### 系统设计

#### 队列结构
```python
_task_queue = queue.Queue()  # 全局队列
_worker_thread = None         # 后台工作线程
```

#### 启动机制
- Django app 启动时调用 `start_worker()`
- 创建一个后台线程，执行 `_worker_loop()`
- 线程一直监听 `_task_queue` 中的任务

#### 任务类型

| 任务类型 | 触发点 | 处理函数 |
|---------|--------|---------|
| training | 上传模型 | `_process_training()` |
| prediction | 创建预测任务 | `_process_prediction()` |

### 关键函数

#### `enqueue_training(model_id, base_folder)`
- 入队训练任务
- 参数：模型 ID、基础文件夹路径
- 返回：无
- 效果：立即返回（异步）

#### `_process_training()`
- 实际执行训练
- 读取模型关联的数据集
- 加载 CSV 数据
- 执行训练逻辑
- 更新模型状态

```python
def _process_training(model_id, base_folder):
    try:
        # 从数据库获取模型
        model = MLModel.objects.get(id=model_id)
        
        # 获取关联的数据集
        dataset = model.dataset
        
        # 读取 CSV 数据
        csv_path = dataset.file_path
        df = pd.read_csv(csv_path)
        
        # 训练模型（demo）
        target_col = model.target_column
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # 实际训练或加载预训练模型...
        
        # 生成指标
        metrics = {
            "accuracy": 0.95,
            "precision": 0.93,
            "recall": 0.91
        }
        
        # 保存结果
        model.status = 'completed'
        model.training_time = elapsed_time
        model.save()
        
    except Exception as e:
        model.status = 'failed'
        model.save()
```

#### `enqueue_prediction(task_id, ...)`
- 入队预测任务
- 执行多模型预测并生成结果 JSON

---

## 文件存储结构

### 存储目录

```
backend/
├── models_storage/
│   └── {model_id}/
│       ├── model.pkl          # joblib 保存的模型
│       └── metrics.txt        # 评估指标（纯文本）
│
├── datasets_storage/          # ✨ 新增
│   └── {dataset_id}/
│       └── dataset.csv        # 上传的 CSV 文件
│
└── predictions_storage/
    └── {task_id}/
        └── result.json        # 预测结果（JSON 格式）
```

### 文件格式

#### metrics.txt 示例
```
Model: 预测模型v1
Training Time: 300.5 seconds

Metrics:
Accuracy: 0.95
Precision: 0.93
Recall: 0.91
F1-Score: 0.92
```

#### result.json 示例
```json
{
  "task_id": 1,
  "origin": "北京",
  "destination": "上海",
  "created_at": "2026-05-09T10:00:00Z",
  "completed_at": "2026-05-09T10:05:30Z",
  "summary": {
    "baseline_price": 1000,
    "best_prediction": 1050,
    "avg_prediction": 1033,
    "std_deviation": 25.3
  },
  "models": [
    {
      "id": 1,
      "name": "模型A",
      "prediction": 1050,
      "confidence": 0.92,
      "ranking": 1
    },
    {
      "id": 2,
      "name": "模型B",
      "prediction": 1033,
      "confidence": 0.88,
      "ranking": 2
    }
  ]
}
```

---

## 配置和部署

### 开发环境设置

#### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.\.venv\Scripts\Activate.ps1

# 激活虚拟环境（macOS/Linux）
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 执行迁移
python manage.py makemigrations
python manage.py migrate

# 启动开发服务器（端口 8001）
python manage.py runserver 127.0.0.1:8001
```

#### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

**Vite 开发代理配置**:
```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8001',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '/api')
  }
}
```

### 生产环境部署

#### 使用 Gunicorn + Nginx

```bash
# 1. 安装 Gunicorn
pip install gunicorn

# 2. 前端打包
cd frontend
npm run build

# 3. 启动后端（多进程）
cd backend
gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 120 freight.wsgi

# 4. 配置 Nginx 反向代理（示例）
```

**Nginx 配置片段**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### 环境变量配置

`backend/freight/settings.py` 中修改：

```python
# 数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 允许的主机
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'your-domain.com']

# 调试模式
DEBUG = False  # 生产环境关闭

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 数据库备份

```bash
# SQLite 备份
cp backend/db.sqlite3 backend/db.sqlite3.backup.$(date +%Y%m%d)

# 恢复
cp backend/db.sqlite3.backup.20260509 backend/db.sqlite3
```

---

## 常见问题

### Q1: 前端提示 "Axios error: 404"，无法连接后端？
**A**: 
1. 确保后端运行在 `127.0.0.1:8001` 上
2. 检查 Vite 配置中的代理是否正确
3. 查看浏览器控制台 Network 标签，确认请求 URL
4. 后端和前端应该同时运行

### Q2: 数据集上传后为什么看不到列名？
**A**: 检查 CSV 文件首行是否包含列名，确保不是从第二行开始的数据

### Q3: 如何修改已上传的 target 列？
**A**: 进入 Datasets 页面 → 点击数据集"详情" → 在 Target 列下拉框中选择新列 → 点击"保存"

### Q4: 模型训练一直显示 "training" 不完成？
**A**: 
1. 检查后端控制台是否有错误输出
2. 确保数据集文件存在且可读
3. 重启 Django 服务试试

### Q5: 预测任务提示 "target_column 不匹配"？
**A**: 所有选中的模型 target 列必须相同，请检查模型关联的数据集和 target 列设置

### Q6: 前端 npm run build 报错？
**A**: 清理缓存重试
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Q7: SQLite 数据库锁定（database is locked）？
**A**: 
1. 关闭所有 Django 进程
2. 删除 `db.sqlite3-journal` 文件
3. 重启服务

### Q8: 如何导出预测结果？
**A**: History 页面 → 选择任务 → 点击"下载 JSON" → result.json 文件下载

### Q9: 生产环境下传输大型数据集会超时？
**A**: 在 Gunicorn 启动参数中增加超时时间：
```bash
gunicorn --timeout 300 ...
```

### Q10: 如何升级到 Celery 任务队列？
**A**: 
1. 安装 `pip install celery redis`
2. 创建 `celery.py` 配置
3. 替换 `enqueue_training()` 和 `enqueue_prediction()` 为 Celery task
4. 启动 Celery worker

---

**文档最后更新**: 2026-05-09  
**版本**: v2.0 (详细版)  
**主要内容**:
- ✨ 完整数据库表结构与说明
- ✨ 详细 API 接口文档与请求/响应示例
- ✨ 前端页面功能详解与截图指南
- ✨ 核心业务流程图与代码逻辑
- ✨ 任务队列系统详细设计
- ✨ 文件存储结构与格式
- ✨ 生产部署指南与 Nginx 配置
- ✨ 常见问题与解决方案
