"""
LangGraph Agent with MCP Integration
Connects to MCP server and handles user queries
"""

import json
import logging
import subprocess
from typing import Any, Annotated
import sys

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.language_model.llm import LLM
from langchain_core.outputs.chat_generation import ChatGeneration
from langchain_core.outputs.llm_result import LLMResult
from typing_extensions import TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Agent state for LangGraph."""
    messages: list[BaseMessage]
    query: str
    response: str | None


# ============================================================================
# CUSTOM TOOLS
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.
    
    Args:
        expression: A mathematical expression (e.g., '15% of 50000' or '100 + 50')
        
    Returns:
        Calculation result
    """
    try:
        # Handle percentage calculations
        if "%" in expression:
            parts = expression.split(" of ")
            if len(parts) == 2:
                percent_str = parts[0].strip().replace("%", "").strip()
                amount_str = parts[1].strip()
                percent = float(percent_str)
                amount = float(amount_str)
                result = (percent / 100) * amount
                return f"{percent}% of {amount} = {result}"
        
        # Standard calculation
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def formatter(text: str, format_type: str = "json") -> str:
    """
    Format text in various ways.
    
    Args:
        text: Text to format
        format_type: Type of formatting - 'json', 'uppercase', 'lowercase'
        
    Returns:
        Formatted text
    """
    try:
        if format_type == "json":
            # Try to parse and pretty print JSON
            if isinstance(text, str):
                parsed = json.loads(text)
            else:
                parsed = text
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        elif format_type == "uppercase":
            return text.upper()
        elif format_type == "lowercase":
            return text.lower()
        else:
            return f"Unknown format type: {format_type}"
    except Exception as e:
        return f"Error formatting: {str(e)}"


# ============================================================================
# MOCK LLM
# ============================================================================

class MockLLM(LLM):
    """Mock LLM that simulates tool calling based on user query."""
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> LLMResult:
        """Generate mock LLM response with tool calling."""
        last_message = messages[-1].content.lower()
        
        # Route to appropriate tools based on query
        if "список" in last_message or "все продукты" in last_message or "show products" in last_message:
            tool_use = json.dumps({
                "tool": "list_products",
                "args": {}
            })
            content = f"I'll get all products for you. [TOOL_USE: {tool_use}]"
        
        elif "категория" in last_message or "category" in last_message or "электроника" in last_message:
            category = "Электроника" if "электроника" in last_message else "Электроника"
            tool_use = json.dumps({
                "tool": "list_products",
                "args": {"category": category}
            })
            content = f"Getting products in {category} category. [TOOL_USE: {tool_use}]"
        
        elif "статистика" in last_message or "statistics" in last_message or "средняя цена" in last_message:
            tool_use = json.dumps({
                "tool": "get_statistics"
            })
            content = f"Getting product statistics. [TOOL_USE: {tool_use}]"
        
        elif "product id" in last_message or "товар" in last_message or "найти" in last_message:
            # Extract product ID from query
            words = last_message.split()
            product_id = None
            for i, word in enumerate(words):
                if word in ["id", "номер"] and i + 1 < len(words):
                    try:
                        product_id = int(words[i + 1])
                        break
                    except:
                        pass
            if product_id:
                tool_use = json.dumps({
                    "tool": "get_product",
                    "args": {"product_id": product_id}
                })
                content = f"Getting product with ID {product_id}. [TOOL_USE: {tool_use}]"
            else:
                content = "Please specify a product ID."
        
        elif "добавь" in last_message or "add" in last_message or "новый" in last_message:
            # Try to parse product details
            content = "I'll help you add a new product. Please provide name, price, and category."
        
        elif "%" in last_message or "посчитай" in last_message or "calculate" in last_message or "discount" in last_message:
            # Extract calculation from query
            if "%" in last_message:
                parts = last_message.split("%")
                if parts:
                    # Try to find the percentage value
                    expr = parts[0].strip().split()[-1] + "% of " + parts[1].strip().split()[-1]
                    tool_use = json.dumps({
                        "tool": "calculator",
                        "args": {"expression": expr}
                    })
                    content = f"Calculating discount. [TOOL_USE: {tool_use}]"
                else:
                    content = "I can help calculate discounts and prices."
            else:
                content = "I can help with calculations. Please specify the expression."
        
        else:
            content = "I'll help you with product management. What would you like to do?"
        
        generation = ChatGeneration(message=AIMessage(content=content))
        return LLMResult(generations=[[generation]])
    
    @property
    def _llm_type(self) -> str:
        return "mock"


# ============================================================================
# MCP CLIENT
# ============================================================================

class MCPClient:
    """Client to communicate with MCP server via stdio."""
    
    def __init__(self, mcp_process: subprocess.Popen):
        self.process = mcp_process
        self.request_id = 0
    
    def call_tool(self, tool_name: str, args: dict) -> Any:
        """Call a tool on the MCP server."""
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line.encode())
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline().decode().strip()
        if response_line:
            response = json.loads(response_line)
            if "result" in response:
                return response["result"]
            elif "error" in response:
                raise Exception(f"MCP Error: {response['error']}")
        
        return None


# ============================================================================
# AGENT EXECUTION
# ============================================================================

def process_user_query(query: str, mcp_client: MCPClient | None = None) -> str:
    """Process user query and return response."""
    logger.info(f"Processing query: {query}")
    
    response_parts = []
    
    # Determine which tool to use based on query
    query_lower = query.lower()
    
    try:
        if "список" in query_lower or "все продукты" in query_lower or "show products" in query_lower:
            result = mcp_client.call_tool("list_products", {}) if mcp_client else {"products": []}
            response_parts.append(f"Products: {json.dumps(result, ensure_ascii=False)}")
        
        elif "категория" in query_lower or "category" in query_lower or "электроника" in query_lower:
            category = "Электроника"
            result = mcp_client.call_tool("list_products", {"category": category}) if mcp_client else {"products": []}
            response_parts.append(f"Products in {category}: {json.dumps(result, ensure_ascii=False)}")
        
        elif "статистика" in query_lower or "statistics" in query_lower or "средняя цена" in query_lower:
            result = mcp_client.call_tool("get_statistics", {}) if mcp_client else {}
            response_parts.append(f"Statistics: {json.dumps(result, ensure_ascii=False)}")
        
        elif "product" in query_lower or "товар" in query_lower or "id" in query_lower:
            # Extract product ID
            words = query_lower.split()
            for i, word in enumerate(words):
                if word == "id" and i + 1 < len(words):
                    try:
                        product_id = int(words[i + 1])
                        result = mcp_client.call_tool("get_product", {"product_id": product_id}) if mcp_client else {}
                        response_parts.append(f"Product {product_id}: {json.dumps(result, ensure_ascii=False)}")
                        break
                    except:
                        pass
        
        elif "добавь" in query_lower or "add product" in query_lower or "новый" in query_lower:
            response_parts.append("To add a product, please provide: name, price, category, and in_stock status.")
        
        elif "%" in query_lower or "скидка" in query_lower or "discount" in query_lower:
            # Use calculator tool
            calc_result = calculator("15% of 50000")
            response_parts.append(f"Calculation: {calc_result}")
        
        else:
            response_parts.append("How can I help you with product management?")
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        response_parts.append(f"Error: {str(e)}")
    
    return " ".join(response_parts)


def create_agent():
    """Create and configure the LangGraph agent."""
    workflow = StateGraph(AgentState)
    
    # Define nodes
    def process_node(state: AgentState) -> AgentState:
        """Process user query through MCP and tools."""
        logger.info(f"Processing: {state['query']}")
        response = process_user_query(state['query'])
        return {
            **state,
            "response": response
        }
    
    # Add nodes
    workflow.add_node("process", process_node)
    workflow.set_entry_point("process")
    workflow.add_edge("process", END)
    
    # Compile agent
    return workflow.compile()


def run_agent(query: str) -> str:
    """Run the agent with a user query."""
    agent = create_agent()
    
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)],
        "query": query,
        "response": None
    }
    
    result = agent.invoke(initial_state)
    return result.get("response", "No response generated")
