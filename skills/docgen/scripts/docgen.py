#!/usr/bin/env python3
"""
Document Generation via AWS Bedrock AgentCore Runtime.

Generates pptx, docx, pdf, xlsx, or html files using a remote
AgentCore Runtime agent (Claude + Code Interpreter).

Usage:
    python3 docgen.py --type pptx --prompt "Create a 10-slide deck about AI" --output slides.pptx
    python3 docgen.py --type docx --prompt "Write a technical report" --output report.docx
    python3 docgen.py --type pptx --prompt-file prompt.txt --output deck.pptx

Environment variables:
    AWS_REGION      - AWS region (default: ap-northeast-1)
    RUNTIME_ARN     - AgentCore Runtime ARN (required)
    AWS credentials - From ~/.aws/credentials, env vars, or IAM role

Optionally reads .env from ~/codes/document-generation-mcp/.env if present.
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

VALID_TYPES = {"docx", "pdf", "pptx", "xlsx", "frontend-design"}

# Try loading .env from document-generation-mcp project (optional)
for _env_candidate in [
    Path.home() / "codes" / "document-generation-mcp" / ".env",
    Path(__file__).resolve().parent.parent / ".env",
]:
    if _env_candidate.exists():
        for line in _env_candidate.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())
        break

DEFAULT_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
DEFAULT_RUNTIME_ARN = os.environ.get("RUNTIME_ARN", "")


def generate(skill_type, prompt, output_path, region=None, runtime_arn=None,
             read_timeout=1200):
    """Generate a document via AgentCore Runtime.

    Args:
        skill_type: One of docx, pdf, pptx, xlsx, frontend-design
        prompt: Description of the document to create
        output_path: Where to save the generated file
        region: AWS region (default from env)
        runtime_arn: AgentCore Runtime ARN (default from env)
        read_timeout: HTTP read timeout in seconds (default 1200)

    Returns:
        dict with keys: success (bool), path (str), size (int), elapsed (float)
    """
    import boto3
    from botocore.config import Config

    region = region or DEFAULT_REGION
    runtime_arn = runtime_arn or DEFAULT_RUNTIME_ARN

    if not runtime_arn:
        return {"success": False, "error": "RUNTIME_ARN not configured. Set via env var or --runtime-arn."}

    if skill_type not in VALID_TYPES:
        return {"success": False, "error": f"Invalid type: {skill_type}. Valid: {sorted(VALID_TYPES)}"}

    client = boto3.client(
        "bedrock-agentcore",
        region_name=region,
        config=Config(read_timeout=read_timeout, connect_timeout=30),
    )

    payload = json.dumps({
        "skill_type": skill_type,
        "prompt": prompt,
        "filename": os.path.basename(output_path),
    })

    start = time.time()

    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            payload=payload,
            contentType="application/json",
            accept="application/json",
        )

        body = response.get("response")
        if body is None:
            return {"success": False, "error": "Empty response from AgentCore", "elapsed": time.time() - start}

        data = body.read() if hasattr(body, "read") else body
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        result = json.loads(data)
        elapsed = time.time() - start

        if result.get("status") == "success" and "file_base64" in result:
            file_bytes = base64.b64decode(result["file_base64"])
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(file_bytes)
            return {
                "success": True,
                "path": output_path,
                "size": len(file_bytes),
                "elapsed": elapsed,
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "No file in response"),
                "elapsed": elapsed,
            }

    except Exception as e:
        return {"success": False, "error": str(e), "elapsed": time.time() - start}


def main():
    parser = argparse.ArgumentParser(description="Generate documents via AgentCore Runtime")
    parser.add_argument("--type", dest="skill_type", choices=sorted(VALID_TYPES), required=True,
                        help="Document type to generate")
    parser.add_argument("--prompt", help="Document description")
    parser.add_argument("--prompt-file", help="Read prompt from file")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--region", default=DEFAULT_REGION, help=f"AWS region (default: {DEFAULT_REGION})")
    parser.add_argument("--runtime-arn", default=DEFAULT_RUNTIME_ARN, help="AgentCore Runtime ARN")
    parser.add_argument("--timeout", type=int, default=1200, help="Read timeout in seconds (default: 1200)")

    args = parser.parse_args()

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("Error: --prompt or --prompt-file required", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {args.skill_type} \u2192 {args.output}")
    print(f"Prompt length: {len(prompt)} chars")

    result = generate(
        skill_type=args.skill_type,
        prompt=prompt,
        output_path=args.output,
        region=args.region,
        runtime_arn=args.runtime_arn,
        read_timeout=args.timeout,
    )

    if result["success"]:
        size_kb = result["size"] / 1024
        mins, secs = divmod(int(result["elapsed"]), 60)
        print(f"Saved: {result['path']} ({size_kb:.1f} KB) in {mins}m {secs}s")
    else:
        print(f"Failed: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
