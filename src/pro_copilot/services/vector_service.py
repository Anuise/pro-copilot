import logging
from pathlib import Path
import uuid
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from pro_copilot.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "skills"

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)

async def get_embedding(text: str) -> list[float]:
    """呼叫 OpenAI API 取得 text-embedding-3-small 的 1536 維向量。"""
    if not settings.openai_api_key or "placeholder" in settings.openai_api_key:
        # 回傳 1536 維的 mock 向量
        return [0.0] * 1536
        
    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

async def init_qdrant_collection() -> None:
    """初始化 Qdrant collection。"""
    client = get_qdrant_client()
    try:
        collections = client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        if not exists:
            logger.info("建立 Qdrant 集合: %s", COLLECTION_NAME)
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )
    except Exception as exc:
        logger.error("初始化 Qdrant 失敗: %s", exc)

async def sync_skills_to_vector_db() -> int:
    """讀取 vault/skills/*.md 並同步至 Qdrant。"""
    await init_qdrant_collection()
    skills_dir: Path = settings.vault_dir / "skills"
    if not skills_dir.exists():
        return 0

    client = get_qdrant_client()
    points = []
    count = 0

    for filepath in skills_dir.glob("*.md"):
        if filepath.name == ".gitkeep":
            continue
        content = filepath.read_text(encoding="utf-8")
        if not content.strip():
            continue
        
        # 取得 embedding
        try:
            vector = await get_embedding(content)
            # 使用檔名的 hash 作為 UUID 以避免重複 upsert
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, filepath.name))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "filename": filepath.name,
                        "title": filepath.stem,
                        "content": content
                    }
                )
            )
            count += 1
        except Exception as exc:
            logger.error("無法將檔案 %s 向量化: %s", filepath.name, exc)

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info("成功同步 %d 個技能卡片至 Qdrant。", len(points))
    
    return count

async def search_relevant_skills(query_text: str, limit: int = 5) -> list[dict]:
    """在 Qdrant 中檢索與 query_text 相似的技能卡片。"""
    await init_qdrant_collection()
    client = get_qdrant_client()
    
    try:
        # 如果 Qdrant collection 中沒有任何點，先自動進行一次同步
        info = client.get_collection(COLLECTION_NAME)
        if info.points_count == 0:
            logger.info("Qdrant 中無資料，自動啟動技能同步...")
            await sync_skills_to_vector_db()
            info = client.get_collection(COLLECTION_NAME)
            if info.points_count == 0:
                return []
    except Exception as exc:
        logger.error("取得 Qdrant collection 資訊失敗: %s", exc)
        return []

    try:
        query_vector = await get_embedding(query_text)
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )
        return [r.payload for r in results if r.payload]
    except Exception as exc:
        logger.error("Qdrant 檢索失敗: %s", exc)
        return []
