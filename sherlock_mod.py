import aiohttp
import asyncio
import json
from typing import List, Tuple

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def check_site(session, site_info, username) -> Tuple[str, str] | None:
    """
    site_info: {"name": "Twitter", "url": "https://twitter.com/{}", "errorType": "status_code", ...}
    Возвращает (site_name, url) если найден, иначе None.
    """
    name = site_info["name"]
    url_template = site_info["url"]
    url = url_template.format(username)

    try:
        async with session.get(url, timeout=10, allow_redirects=True) as resp:
            if resp.status == 200:
                # Базовая проверка: статус 200 считаем найденным, но можно добавить доп. условия из json (например, проверка текста)
                return (name, url)
    except Exception:
        pass
    return None

async def sherlock_search(username: str, timeout: int = 30) -> List[Tuple[str, str]]:
    with open("sites.json", "r", encoding="utf-8") as f:
        sites = json.load(f)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [check_site(session, site, username) for site in sites]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]