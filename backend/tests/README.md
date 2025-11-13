# 後端測試說明

## 目錄結構

```
backend/tests/
├── unit/           # 單元測試 - 測試單一函數或類別
├── integration/    # 整合測試 - 測試多個模組間的互動
└── fixtures/       # 測試固定數據 (fixtures)
```

## 單元測試 (unit/)

測試單一函數、類別或模組的功能，不依賴外部服務。

**範例**:
- 測試密碼加密函數
- 測試 JWT token 生成
- 測試文件分塊邏輯
- 測試權限檢查函數

## 整合測試 (integration/)

測試多個模組之間的互動，可能需要資料庫或外部服務。

**範例**:
- 測試文件上傳 + 解析 + 向量化流程
- 測試 RAG 問答完整流程
- 測試使用者認證 + 權限檢查
- 測試群組成員管理功能

## 測試固定數據 (fixtures/)

提供測試所需的固定數據，如模擬的使用者、文件、對話等。

**範例**:
- 測試用的 PDF 檔案
- 模擬的使用者資料
- 模擬的群組資料
- 模擬的向量資料

## 執行測試

```bash
# 執行所有測試
pytest

# 執行單元測試
pytest tests/unit/

# 執行整合測試
pytest tests/integration/

# 執行特定測試文件
pytest tests/unit/test_auth.py

# 顯示詳細輸出
pytest -v

# 顯示測試覆蓋率
pytest --cov=app
```

## 測試命名規範

- 測試文件: `test_*.py`
- 測試函數: `test_*`
- 測試類別: `Test*`

**範例**:
```python
# tests/unit/test_auth.py
def test_password_hashing():
    """測試密碼加密功能"""
    pass

def test_verify_password():
    """測試密碼驗證功能"""
    pass

class TestJWT:
    """測試 JWT 相關功能"""

    def test_create_access_token(self):
        """測試 JWT token 生成"""
        pass

    def test_decode_access_token(self):
        """測試 JWT token 解碼"""
        pass
```
