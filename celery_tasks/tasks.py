from celery_app_worker import celery_app
import asyncio
import httpx

from celery_tasks.client import MCPOpenAIClient  

@celery_app.task
def process_message_task(message: str, client_id: int):
    async def process_with_mcp():
        client = MCPOpenAIClient()
        # Connect to the MCP server running on localhost:8050 using SSE
        await client.connect_to_server("http://mcp-server:8050/sse")
        response = await client.process_query(message)
        await client.cleanup()
        return response

    bot_response = asyncio.run(process_with_mcp())

    # Call the FastAPI webhook to send the response to the client
    httpx.post(
        "http://fastapi_app:8000/webhook/task-complete",
        json={"client_id": client_id, "response": bot_response},
        timeout=5.0
    )
