from agents import Agent, Runner, set_tracing_disabled
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from model import get_model
from textwrap import dedent
import os
import logging

logging.basicConfig(level="DEBUG")

set_tracing_disabled(True)

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

polars_server = MCPServerStreamableHttp(
    params = MCPServerStreamableHttpParams(
        url=f"http://localhost:8000/mcp",
        timeout=30
    ),
    client_session_timeout_seconds=30,
)

polars_agent = Agent(
    name="Polars Questions Agent",
    instructions = dedent("""
        You are an agent that helps users with questions
        related to Polars data analysis Python framework.

        Think step by step:

        - User will ask a question
        - Transform that into a query that is suited for Full Text Search on top of Polars docs
            - Try to only use terms related to Polars class names and functions,
              excluding other words. Examples:
              Examples:
                - User: "How do I filter a DataFrame in Polars?"
                    query: "dataframe filter"
                - User: "What is the difference between `select` and `with_columns`?"
                    query: "select with_columns"
                - User: "Group by examples"
                    query: "groupby"
            - If you get no results, try using a different variation of the query
        - Consolidate the results and answer the user's initial question with the results obtained

        Important: ONLY provide the answers based on data fetched via the provided tools.

        Finally, provide the reference URL(s) that you used to come up with your answer at the end.

    """),
    model=get_model()
)

async def main():

    async with polars_server as mcp_server:
        polars_agent.mcp_servers = [mcp_server]
        input_ = input("Tell me your Polars question: ")
        result = await Runner.run(starting_agent=polars_agent, input=input_)
        return result.final_output


if __name__ == "__main__":

    import asyncio
    result = asyncio.run(main())
    print(result)