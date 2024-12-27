import os
import requests
from lagent.actions.base_action import BaseAction, tool_api
from lagent.schema import ActionReturn, ActionStatusCode

class WeatherQuery(BaseAction):
    def __init__(self):
        super().__init__()
        self.api_key = "bab076362a08430299755aea1f366722"
        print(self.api_key)
        if not self.api_key:
            raise EnvironmentError("未找到环境变量 'token'。请设置你的和风天气 API Key 到 'weather_token' 环境变量中，比如export weather_token='xxx' ")

    @tool_api
    def run(self, location: str) -> dict:
        """
        查询实时天气信息。

        Args:
            location (str): 要查询的地点名称、LocationID 或经纬度坐标（如 "101010100" 或 "116.41,39.92"）。

        Returns:
            dict: 包含天气信息的字典
                * location: 地点名称
                * weather: 天气状况
                * temperature: 当前温度
                * wind_direction: 风向
                * wind_speed: 风速（公里/小时）
                * humidity: 相对湿度（%）
                * report_time: 数据报告时间
        """
        try:
            # 如果 location 不是坐标格式（例如 "116.41,39.92"），则调用 GeoAPI 获取 LocationID
            if not ("," in location and location.replace(",", "").replace(".", "").isdigit()):
                # 使用 GeoAPI 获取 LocationID
                geo_url = f"https://geoapi.qweather.com/v2/city/lookup?location={location}&key={self.api_key}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()

                if geo_data.get("code") != "200" or not geo_data.get("location"):
                    raise Exception(f"GeoAPI 返回错误码：{geo_data.get('code')} 或未找到位置")

                location = geo_data["location"][0]["id"]

            # 构建天气查询的 API 请求 URL
            weather_url = f"https://devapi.qweather.com/v7/weather/now?location={location}&key={self.api_key}"
            response = requests.get(weather_url)
            data = response.json()

            # 检查 API 响应码
            if data.get("code") != "200":
                raise Exception(f"Weather API 返回错误码：{data.get('code')}")

            # 解析和组织天气信息
            weather_info = {
                "location": location,
                "weather": data["now"]["text"],
                "temperature": data["now"]["temp"] + "°C", 
                "wind_direction": data["now"]["windDir"],
                "wind_speed": data["now"]["windSpeed"] + " km/h",  
                "humidity": data["now"]["humidity"] + "%",
                "report_time": data["updateTime"]
            }

            return {"result": weather_info}

        except Exception as exc:
            return ActionReturn(
                errmsg=f"WeatherQuery 异常：{exc}",
                state=ActionStatusCode.HTTP_ERROR
            )