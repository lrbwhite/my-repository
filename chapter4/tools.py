from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

import os
from tavily import TavilyClient
from typing import Dict, Any

def search(query: str) -> str:
    """
    基于 Tavily 的网页搜索引擎工具。
    优先返回 Tavily 的AI总结答案，无直接答案时返回前3条搜索结果摘要。
    """
    print(f"🔍 正在执行 [Tavily] 网页搜索: {query}")
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if api_key:
            api_key = api_key.strip()   # 清除换行、空格、制表符
        if not api_key:
            return "错误：TAVILY_API_KEY 未在 .env 文件中配置。"

        client = TavilyClient(api_key=api_key)
        resp = client.search(
            query=query + ",请用中文给出答案",
            search_depth="basic",
            max_results=5,
            include_answer=True,
            include_raw_content=False,
        )

        # 优先 Tavily 生成的直接答案
        if resp.get("answer"):
            return resp["answer"]

        # 没有直接答案，取前3条网页结果摘要
        results = resp.get("results", [])
        if results:
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('content', '')}"
                for i, res in enumerate(results[:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"
    
from typing import Dict, Any

class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")
        
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])


# --- 工具初始化与使用示例 ---
if __name__ == '__main__':
    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)
    
    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4. 智能体的Action调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")