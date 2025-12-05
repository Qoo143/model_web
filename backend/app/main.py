"""
FastAPI 應用程式入口

這是後端應用的主檔案，負責:
- 初始化 FastAPI 應用
- 配置中介軟體（CORS）
- 註冊路由
- 提供健康檢查端點
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# ============================================
# 建立 FastAPI 應用
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基於 RAG 的智能文件問答系統",
    docs_url="/docs",   # Swagger UI 文件路徑
    redoc_url="/redoc"  # ReDoc 文件路徑
)

# ============================================
# CORS 中介軟體配置 (強化安全性)
# ============================================
# 允許前端（Vue）跨域請求後端 API
# 安全原則: 僅允許必要的方法和 Header，避免使用萬用字元 (*)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,           # 明確指定允許的來源 (不使用 *)
    allow_credentials=True,                        # 允許攜帶憑證（JWT Token）
    allow_methods=["GET", "POST", "PUT", "DELETE"], # 僅允許必要的 HTTP 方法
    allow_headers=["Content-Type", "Authorization"], # 僅允許必要的 Header
    expose_headers=["Content-Type"],               # 允許前端讀取的 Response Header
    max_age=3600,                                  # Preflight 請求快取時間 (1小時)
)

# ============================================
# 根路徑
# ============================================
@app.get("/")
def root():
    """
    根路徑端點

    返回歡迎訊息和基本資訊
    """
    return {
        "message": f"歡迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "運行中"
    }

# ============================================
# 健康檢查端點
# ============================================
@app.get("/health")
def health_check():
    """
    健康檢查端點

    用於:
    - Docker 健康檢查
    - 監控系統
    - 負載平衡器

    返回應用程式狀態
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# ============================================
# 應用程式生命週期事件
# ============================================
@app.on_event("startup")
async def startup_event():
    """
    應用程式啟動時執行

    業務邏輯:
    - 初始化資料庫連線
    - 載入 ML 模型（未來）
    - 其他初始化任務
    """
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 啟動中...")
    print(f"📝 API 文件: http://localhost:8000/docs")
    # TODO: 初始化資料庫
    # from app.core.database import init_db
    # await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """
    應用程式關閉時執行

    業務邏輯:
    - 關閉資料庫連線
    - 釋放資源
    """
    print(f"👋 {settings.APP_NAME} 正在關閉...")
    # TODO: 關閉資料庫
    # from app.core.database import close_db
    # await close_db()

# ============================================
# 註冊路由
# ============================================
from app.api import auth, groups, documents, chat, debug

# 註冊認證路由
app.include_router(auth.router, prefix="/api")

# 註冊群組管理路由
app.include_router(groups.router, prefix="/api")

# 註冊文件管理路由
app.include_router(documents.router, prefix="/api")

# 註冊對話管理路由
app.include_router(chat.router, prefix="/api")

# 註冊調試路由
app.include_router(debug.router, prefix="/api")

# ============================================
# 開發模式啟動
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # 開發模式自動重載
    )
