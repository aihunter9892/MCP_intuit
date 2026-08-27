from mcp.server import MCPServer

mcp = MCPServer("Hello World Server")


@mcp.tool()
def hello(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()