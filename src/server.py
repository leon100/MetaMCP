"""MCP server implementation with Meta tools."""


from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import settings
from .errors import MetaMCPError
from .logging_config import logger
from .meta_client import MetaClient
from .models import MetaError, MetaResponse, Platform
from .validators import (
    validate_get_messages_request,
    validate_post_content_request,
    validate_whatsapp_recipient,
)

# Initialize MCP server
server = Server("meta-mcp-server")
meta_client = MetaClient(settings)


# Tool Definitions


@server.list_tools()  # type: ignore
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="meta_send_message",
            description="Send a message to a recipient on Facebook, Instagram, or WhatsApp",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["facebook", "instagram", "whatsapp"],
                        "description": "Target platform",
                    },
                    "recipient_id": {
                        "type": "string",
                        "description": "Recipient ID (PSID for FB/IG, E.164 phone for WhatsApp)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Message text content",
                    },
                    "media_url": {
                        "type": "string",
                        "description": "Optional media URL to attach",
                    },
                },
                "required": ["platform", "recipient_id", "content"],
            },
        ),
        Tool(
            name="meta_get_messages",
            description="Retrieve message history from a conversation (FB/IG only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["facebook", "instagram", "whatsapp"],
                        "description": "Target platform",
                    },
                    "conversation_id": {
                        "type": "string",
                        "description": "Conversation ID",
                    },
                    "recipient_id": {
                        "type": "string",
                        "description": "Recipient ID (alternative to conversation_id)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of messages to retrieve (1-100)",
                        "default": 10,
                    },
                },
                "required": ["platform"],
            },
        ),
        Tool(
            name="meta_post_content",
            description="Post content to Facebook or Instagram feed",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["facebook", "instagram"],
                        "description": "Target platform (FB or IG only)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content or caption",
                    },
                    "media_urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Media URLs to post",
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Optional target page/account ID",
                    },
                },
                "required": ["platform"],
            },
        ),
        Tool(
            name="meta_get_analytics",
            description="Retrieve analytics/insights from Facebook or Instagram",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["facebook", "instagram"],
                        "description": "Target platform (FB or IG only)",
                    },
                    "metric": {
                        "type": "string",
                        "enum": ["impressions", "reach", "engagement", "followers", "profile_views"],
                        "description": "Metric to retrieve",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["day", "week", "month"],
                        "default": "day",
                        "description": "Time period for analytics",
                    },
                },
                "required": ["platform", "metric"],
            },
        ),
    ]


@server.call_tool()  # type: ignore
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "meta_send_message":
            return await handle_send_message(arguments)
        elif name == "meta_get_messages":
            return await handle_get_messages(arguments)
        elif name == "meta_post_content":
            return await handle_post_content(arguments)
        elif name == "meta_get_analytics":
            return await handle_get_analytics(arguments)
        else:
            error = MetaError(
                error_code="UNKNOWN_TOOL",
                error_message=f"Unknown tool: {name}",
                platform="unknown",
            )
            return [TextContent(type="text", text=error.model_dump_json())]
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}", exc_info=True)
        error = MetaError(
            error_code="EXECUTION_ERROR",
            error_message=str(e),
            platform=arguments.get("platform", "unknown"),
        )
        return [TextContent(type="text", text=error.model_dump_json())]


# Tool Handlers


async def handle_send_message(args: dict[str, Any]) -> list[TextContent]:
    """Handle meta_send_message tool."""
    platform: Platform = args["platform"]
    recipient_id: str = args["recipient_id"]
    content: str = args["content"]
    media_url: str | None = args.get("media_url")

    try:
        # WhatsApp-specific validation
        if platform == "whatsapp":
            validate_whatsapp_recipient(recipient_id)

        adapter = meta_client.get_adapter(platform)
        result = await adapter.send_message(recipient_id, content, media_url)

        response = MetaResponse(
            success=True, platform=platform, data=result, message="Message sent successfully"
        )
        return [TextContent(type="text", text=response.model_dump_json())]

    except MetaMCPError as e:
        error = MetaError(
            error_code=e.error_code,
            error_message=e.message,
            platform=platform,
        )
        return [TextContent(type="text", text=error.model_dump_json())]


async def handle_get_messages(args: dict[str, Any]) -> list[TextContent]:
    """Handle meta_get_messages tool."""
    platform: Platform = args["platform"]
    conversation_id: str | None = args.get("conversation_id")
    recipient_id: str | None = args.get("recipient_id")
    limit: int = args.get("limit", 10)

    try:
        validate_get_messages_request(conversation_id, recipient_id)

        adapter = meta_client.get_adapter(platform)
        messages = await adapter.get_messages(conversation_id, recipient_id, limit)

        response = MetaResponse(
            success=True,
            platform=platform,
            data=messages,
            message=f"Retrieved {len(messages)} messages",
        )
        return [TextContent(type="text", text=response.model_dump_json())]

    except MetaMCPError as e:
        error = MetaError(
            error_code=e.error_code,
            error_message=e.message,
            platform=platform,
        )
        return [TextContent(type="text", text=error.model_dump_json())]


async def handle_post_content(args: dict[str, Any]) -> list[TextContent]:
    """Handle meta_post_content tool."""
    platform: Platform = args["platform"]
    content: str | None = args.get("content")
    media_urls: list[str] | None = args.get("media_urls")
    target_id: str | None = args.get("target_id")

    try:
        validate_post_content_request(platform, content, media_urls)

        adapter = meta_client.get_adapter(platform)
        result = await adapter.post_content(content, media_urls, target_id)

        response = MetaResponse(
            success=True, platform=platform, data=result, message="Content posted successfully"
        )
        return [TextContent(type="text", text=response.model_dump_json())]

    except MetaMCPError as e:
        error = MetaError(
            error_code=e.error_code,
            error_message=e.message,
            platform=platform,
        )
        return [TextContent(type="text", text=error.model_dump_json())]


async def handle_get_analytics(args: dict[str, Any]) -> list[TextContent]:
    """Handle meta_get_analytics tool."""
    platform: Platform = args["platform"]
    metric: str = args["metric"]
    period: str = args.get("period", "day")

    try:
        adapter = meta_client.get_adapter(platform)
        result = await adapter.get_analytics(metric, period)

        response = MetaResponse(
            success=True, platform=platform, data=result, message="Analytics retrieved successfully"
        )
        return [TextContent(type="text", text=response.model_dump_json())]

    except MetaMCPError as e:
        error = MetaError(
            error_code=e.error_code,
            error_message=e.message,
            platform=platform,
        )
        return [TextContent(type="text", text=error.model_dump_json())]


async def run_server() -> None:
    """Run the MCP server."""
    logger.info(f"Starting Meta MCP Server (Demo Mode: {settings.demo_mode})")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
