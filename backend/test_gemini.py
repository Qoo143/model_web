"""
Gemini API 獨立測試腳本

不依賴其他專案模組，直接測試 Gemini API
"""

import asyncio
import os

# 嘗試從多個位置讀取 .env
env_paths = ['.env', '../.env', '/app/.env']
for env_path in env_paths:
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"已從 {env_path} 載入環境變數")
        break
    except FileNotFoundError:
        continue

# Gemini API 設定
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')

async def test_gemini():
    """測試 Gemini API"""
    import httpx

    print("=" * 50)
    print("Gemini API 測試")
    print("=" * 50)

    print(f"\n📋 配置:")
    print(f"   模型: {GEMINI_MODEL}")
    print(f"   API Key: {'已設定 (' + GEMINI_API_KEY[:10] + '...)' if GEMINI_API_KEY else '未設定'}")

    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-gemini-api-key':
        print("\n❌ 錯誤: GEMINI_API_KEY 未正確設定")
        print("   請在 .env 檔案中設定有效的 API Key")
        return

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 測試 1: 檢查模型
        print(f"\n🔍 測試 1: 檢查模型可用性...")
        try:
            response = await client.get(
                f"{BASE_URL}/models/{GEMINI_MODEL}?key={GEMINI_API_KEY}"
            )
            if response.status_code == 200:
                print(f"   ✅ 模型 {GEMINI_MODEL} 可用")
            else:
                print(f"   ❌ 模型檢查失敗: {response.status_code}")
                print(f"   {response.text}")
                return
        except Exception as e:
            print(f"   ❌ 請求失敗: {e}")
            return

        # 測試 2: 生成文字
        print(f"\n🔍 測試 2: 文字生成...")
        try:
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "請用一句話介紹什麼是 RAG（Retrieval-Augmented Generation）？請用繁體中文回答。"}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 200
                }
            }

            response = await client.post(
                f"{BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    content = ""
                    for part in candidates[0].get("content", {}).get("parts", []):
                        content += part.get("text", "")

                    usage = data.get("usageMetadata", {})
                    print(f"   ✅ 生成成功")
                    print(f"   Token 數: {usage.get('totalTokenCount', 'N/A')}")
                    print(f"   回答: {content}")
                else:
                    print(f"   ❌ 沒有回應內容")
            else:
                print(f"   ❌ 生成失敗: {response.status_code}")
                print(f"   {response.text}")
                return

        except Exception as e:
            print(f"   ❌ 請求失敗: {e}")
            return

    print("\n" + "=" * 50)
    print("✅ 所有測試通過！Gemini API 運作正常")
    print("=" * 50)


if __name__ == "__main__":
    try:
        import httpx
    except ImportError:
        print("需要安裝 httpx: pip install httpx")
        exit(1)

    asyncio.run(test_gemini())
