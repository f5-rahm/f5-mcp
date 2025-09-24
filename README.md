# F5 MCP Server with mcpo

A Model Context Protocol (MCP) server for F5 BIG-IP devices, served through mcpo. This setup provides AI 
assistants with the ability to query F5 BIG-IP objects like pools, nodes, virtual servers, and other LTM 
components.

## Overview

This repository contains:
- **F5 MCP Server**: A FastMCP-based server that provides tools for querying F5 BIG-IP devices
- **mcpo Integration**: Configuration to serve the MCP server through mcpo for easy integration with AI clients
- **Docker Setup**: Complete containerized environment for both components

## Prerequisites

- Docker and Docker Compose
- F5 BIG-IP device with REST API access
- Network connectivity between the containers and your F5 device

## Quick Start

1. **Clone and prepare the environment:**
   ```bash
   git clone https://github.com/f5-rahm/f5-mcp
   cd f5-mcp
   ```

2. **Create the external Docker network:**
   ```bash
   docker network create labnet
   ```

3. **Configure environment variables:**
   
   Create `f5mcp/.env` file with F5 credentials:
   ```env
   F5_HOST=192.168.1.100
   F5_USER=admin
   F5_PASS=your-password
   ```
   
   Create `.env` file in the main directory with mcpo API key:
   ```env
   MCPO_API_KEY=your-mcpo-api-key-here
   ```

4. **Start the services:**
   ```bash
   docker-compose up -d
   ```
   
   > **Note**: The docker-compose.yml should be configured to use the main `.env` file for the mcpo service. If needed, add `env_file: .env` to the mcpo service definition.

## Project Structure

```
.
├── f5mcp/
│   ├── Dockerfile
│   ├── main.py                 # MCP server implementation
│   ├── requirements.txt
│   └── .env                   # F5 credentials (create this)
├── docker-compose.yml         # Service definitions
├── mcpo-config.json          # mcpo configuration
├── .env                      # mcpo API key (create this)
└── README.md
```

## Testing the MCP Server

### 1. Direct HTTP Testing

Test the MCP server directly using curl or any HTTP client:

**Initialize a session:**
```bash
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "tools": {}
      },
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

**List available tools:**
```bash
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Test the obj_list tool:**
```bash
# List all pools
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "obj_list",
      "arguments": {
        "obj_type": "pool"
      }
    }
  }'

# Get specific pool details
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "obj_list",
      "arguments": {
        "obj_type": "pool",
        "obj_name": "your-pool-name"
      }
    }
  }'
```

### 2. Container Testing

**Check container logs:**
```bash
# F5 MCP Server logs
docker logs f5mcp

# MCPO logs
docker logs mcpo
```

**Test from within the network:**
```bash
# Test MCP server from another container
docker run --rm --network labnet curlimages/curl:latest \
  curl -X POST http://f5mcp:8081/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"clientInfo":{"name":"test","version":"1.0.0"}}}'
```

## Testing mcpo

### 1. Health Check

```bash
# Check if mcpo is running
curl http://localhost:8000/health

# If API key authentication is enabled, include it:
curl -H "Authorization: Bearer your-mcpo-api-key-here" http://localhost:8000/health
```

### 2. List Configured Servers

```bash
curl -X GET http://localhost:8000/servers
```

### 3. Test MCP Server Through mcpo

```bash
# Initialize connection through mcpo
curl -X POST http://localhost:8000/f5mcp/initialize \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }'

# List tools through mcpo
curl -X POST http://localhost:8000/f5mcp/tools/list \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{}'

# Call obj_list through mcpo
curl -X POST http://localhost:8000/f5mcp/tools/call \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "name": "obj_list",
    "arguments": {
      "obj_type": "pool"
    }
  }'
```

> **Note**: If mcpo is configured with API key authentication, add `-H "Authorization: Bearer your-mcpo-api-key-here"` to all curl commands above.

## Available Tools

### `obj_list`

Retrieves F5 BIG-IP LTM objects.

**Parameters:**
- `obj_type` (required): Type of F5 object (e.g., "pool", "node", "virtual", "rule")
- `obj_name` (optional): Specific object name to retrieve details for

**Examples:**
```json
// List all pools
{
  "obj_type": "pool"
}

// Get specific pool details
{
  "obj_type": "pool",
  "obj_name": "web-pool"
}

// List all virtual servers
{
  "obj_type": "virtual"
}
```

## Configuration

### Environment Variables

**F5 MCP Server Configuration** (in `f5mcp/.env`):
- `F5_HOST`: F5 BIG-IP management IP address
- `F5_USER`: F5 username with API access
- `F5_PASS`: F5 user password

**mcpo Configuration** (in `.env`):
- `MCPO_API_KEY`: API key for MCPO authentication (if required)

### mcpo Server Configuration

The mcpo configuration in `mcpo-config.json` defines:

```json
{
  "mcpServers": {
    "f5mcp": {
      "type": "streamable-http",
      "url": "http://f5mcp:8081/mcp",
      "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Connection refused to F5 device:**
   - Verify F5_HOST is reachable from containers
   - Check F5 credentials in `.env` file
   - Ensure F5 device has REST API enabled

2. **mcpo can't connect to MCP server:**
   - Verify both containers are on the `labnet` network
   - Check that f5mcp container is running: `docker ps`
   - Review container logs: `docker logs f5mcp`

3. **Network issues:**
   - Ensure the `labnet` network exists: `docker network ls`
   - Create it if missing: `docker network create labnet`

4. **Missing API keys:**
   - Verify `.env` file exists in main directory with MCPO_API_KEY
   - Check that `f5mcp/.env` contains valid F5 credentials

### Debugging Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs f5mcp
docker-compose logs mcpo

# Test network connectivity
docker exec mcpo ping f5mcp

# Interactive container access
docker exec -it f5mcp /bin/bash
docker exec -it mcpo /bin/bash
```

## Development

### Adding New Tools

To add new tools to the MCP server, modify `f5mcp/main.py`:

```python
@mcp.tool
def your_new_tool(param1: str, param2: int = 10):
    """Description of your tool"""
    # Your implementation here
    return result
```

### Updating Dependencies

Update `f5mcp/requirements.txt` and rebuild:

```bash
docker-compose build f5mcp
docker-compose up -d f5mcp
```

## Integration with AI Clients

This MCP server can be integrated with AI assistants that support the Model Context Protocol. The tools will be available to the AI for querying F5 BIG-IP configurations and status.

Example AI assistant usage:
- "List all pools on the F5 device"
- "Show me the configuration of the web-pool"
- "What virtual servers are configured?"

## Security Considerations

- Store F5 credentials securely (consider using Docker secrets in production)
- Limit network access to the containers
- Use HTTPS for production deployments
- Implement proper authentication for mcpo if needed
- Consider F5 user permissions (read-only recommended for monitoring use cases)

## License

[Apache License 2.0](LICENSE)