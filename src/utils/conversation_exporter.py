"""
Conversation history export utilities.

This module provides functions to export conversation history from
LLMHistoryManager to various file formats (JSON, Markdown) for debugging,
sharing, and analysis purposes.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from providers.llm_history_manager import ChatMessage


def export_to_json(
    messages: List[ChatMessage],
    agent_name: str = "IRIS",
    output_path: Optional[str] = None,
) -> str:
    """
    Export conversation history to JSON format.

    Parameters
    ----------
    messages : List[ChatMessage]
        List of chat messages to export
    agent_name : str, optional
        Name of the agent (default: "IRIS")
    output_path : str, optional
        Path to save the JSON file. If None, uses timestamp-based filename

    Returns
    -------
    str
        Path to the exported JSON file

    Examples
    --------
    >>> messages = [ChatMessage(role="user", content="Hello")]
    >>> path = export_to_json(messages, agent_name="MyBot")
    >>> print(f"Exported to {path}")
    """
    # Generate default filename if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"conversation_history_{timestamp}.json"

    # Prepare export data
    export_data = {
        "metadata": {
            "agent_name": agent_name,
            "export_timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
        },
        "messages": [
            {"role": msg.role, "content": msg.content, "index": idx}
            for idx, msg in enumerate(messages)
        ],
    }

    # Write to file
    output_file = Path(output_path)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully exported {len(messages)} messages to {output_file}")
        return str(output_file.absolute())
    except IOError as e:
        logging.error(f"Failed to write JSON file: {e}")
        raise


def export_to_markdown(
    messages: List[ChatMessage],
    agent_name: str = "IRIS",
    output_path: Optional[str] = None,
) -> str:
    """
    Export conversation history to Markdown format.

    Parameters
    ----------
    messages : List[ChatMessage]
        List of chat messages to export
    agent_name : str, optional
        Name of the agent (default: "IRIS")
    output_path : str, optional
        Path to save the Markdown file. If None, uses timestamp-based filename

    Returns
    -------
    str
        Path to the exported Markdown file

    Examples
    --------
    >>> messages = [ChatMessage(role="user", content="Hello")]
    >>> path = export_to_markdown(messages, agent_name="MyBot")
    >>> print(f"Exported to {path}")
    """
    # Generate default filename if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"conversation_history_{timestamp}.md"

    # Build Markdown content
    lines = [
        "# Conversation History",
        "",
        f"**Agent**: {agent_name}",
        f"**Export Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Messages**: {len(messages)}",
        "",
        "---",
        "",
    ]

    # Handle empty conversation
    if not messages:
        lines.append("*No messages in this conversation.*")
    else:
        for idx, msg in enumerate(messages, start=1):
            lines.append(f"## Message {idx} ({msg.role})")
            lines.append("")
            lines.append(msg.content)
            lines.append("")

    markdown_content = "\n".join(lines)

    # Write to file
    output_file = Path(output_path)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logging.info(f"Successfully exported {len(messages)} messages to {output_file}")
        return str(output_file.absolute())
    except IOError as e:
        logging.error(f"Failed to write Markdown file: {e}")
        raise
