import json
import httpx
from langchain_core.tools import tool
from core.config import settings

@tool
def get_weather(loc: str) -> str:
    """查询指定城市的即时天气。参数 loc: 城市名称，如 Beijing, Shanghai."""

    # 1. 简单映射：把常见城市名转为高德需要的 adcode
    city_adcode_map = {
        "beijing": "110000",
        "shanghai": "310000",
        "guangzhou": "440100",
        "shenzhen": "440300",
    }

    # 如果用户传的是拼音，转成小写去查映射；如果没查到，可以给个默认值或直接返回错误
    city_code = city_adcode_map.get(loc.lower(), loc)

    # 2. 高德天气 API 的固定 URL
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    # 3. 正确的参数：key 和 city (adcode)
    params = {
        "key": settings.gaode_api_key,
        "city": city_code,
        "extensions": "all", # base 表示实况天气，all 表示预报
    }

    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status() # 如果请求失败(4xx/5xx)会抛出异常

        data = response.json()

        # 高德返回的 JSON 如果 status 为 "0" 表示失败
        if data.get("status") == "1":
            forecasts = data.get("forecast")
            if forecasts:
                # 解析 forecasts 数据（forecasts[0] 是当前城市，casts 是预报列表）
                casts = forecasts[0].get("casts",[])
                result_list = []
                for cast in casts:
                    # 提取每天的核心信息
                    date = cast.get("date")
                    day_weather = cast.get("dayweather")
                    day_temp = cast.get('daytemp_float')
                    night_temp = cast.get('nighttemp_float')
                    result_list.append(f'{date}: {day_weather}, {day_temp}℃ ~ {night_temp}℃')
                return json.dumps({'wether_forecast': result_list}, ensure_ascii=False)
            else:
                return json.dumps({'error': '未获取到预报数据'}, ensure_ascii=False)
        else:
            return json.dumps({'error': f'高德API返回错误: {data.get('info')}'}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'error': f'请求失败：{str(e)}'}, ensure_ascii=False)