from google.antigravity import Agent, LocalAgentConfig


async def call_llm(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """使用 Antigravity SDK 啟動 Agent 並回傳生成的文字內容。"""
    config = LocalAgentConfig(system_instructions=system_prompt)

    async with Agent(config) as agent:
        response = await agent.chat(user_prompt)

        content = ""
        async for token in response:
            content += token
        return content
