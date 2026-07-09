#!/usr/bin/env python3
"""
App request capture and spec generation.

This module stores community requests as files under workspace/app_requests.
It does not execute build commands unless APP_REQUEST_AUTOBUILD is explicitly
enabled and APP_REQUEST_BUILD_COMMAND is configured.
"""

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from scripts.deepseek_client import OpenAICompatibleClient


APP_PREFIXES = ("!app", "/app", "app:", "build:", "make:")
APP_KEYWORDS = (
    "build an app",
    "build app",
    "make an app",
    "make app",
    "create an app",
    "create app",
    "build a website",
    "make a website",
    "create a website",
    "build a dashboard",
    "make a dashboard",
    "create a dashboard",
    "build a bot",
    "make a bot",
    "create a bot",
)


@dataclass
class AppRequest:
    request_id: str
    title: str
    description: str
    requester: str
    source: str
    created_at: str
    spec: str
    metadata: dict[str, Any]


def is_app_request(message: str) -> bool:
    """Return True when a message looks like an explicit app request."""
    text = message.strip().lower()
    if not text:
        return False
    if any(text.startswith(prefix) for prefix in APP_PREFIXES):
        return True
    return any(keyword in text for keyword in APP_KEYWORDS)


def strip_app_prefix(message: str) -> str:
    text = message.strip()
    lowered = text.lower()
    for prefix in APP_PREFIXES:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip(" :-\n\t")
    return text


class AppRequestStore:
    """Creates durable request artifacts for app-building workflows."""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace = Path(workspace_path)
        self.requests_dir = self.workspace / "app_requests"
        self.requests_dir.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        description: str,
        requester: str,
        source: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AppRequest:
        clean_description = strip_app_prefix(description)
        created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        request_id = self._request_id(clean_description)
        title = self._title_from_description(clean_description)
        spec = self._generate_spec(clean_description, requester, source)

        request = AppRequest(
            request_id=request_id,
            title=title,
            description=clean_description,
            requester=requester,
            source=source,
            created_at=created_at,
            spec=spec,
            metadata=metadata or {},
        )
        self._write(request)
        self._maybe_autobuild(request)
        return request

    def list_recent(self, limit: int = 5) -> list[AppRequest]:
        requests = []
        for path in sorted(self.requests_dir.glob("*.json"), reverse=True)[:limit]:
            data = json.loads(path.read_text())
            requests.append(AppRequest(**data))
        return requests

    def _request_id(self, description: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        slug = self._slug(description)[:48] or "app-request"
        return f"{timestamp}-{slug}"

    def _title_from_description(self, description: str) -> str:
        words = re.sub(r"\s+", " ", description).strip().split(" ")
        title = " ".join(words[:10]).strip(" .,!?:;")
        return title or "New app request"

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
        return re.sub(r"-{2,}", "-", slug)

    def _generate_spec(self, description: str, requester: str, source: str) -> str:
        system = (
            "You turn messy community app ideas into concise build specs. "
            "Do not promise that code has been built. Identify unknowns and "
            "write a practical MVP that an engineer can execute."
        )
        prompt = f"""
Create a build request spec from this community request.

Requester: {requester}
Source: {source}
Request:
{description}

Return markdown with these headings:
- Summary
- Target Users
- MVP Scope
- Key Screens or Commands
- Data and Integrations
- Acceptance Criteria
- Open Questions
- Suggested Build Plan
"""
        try:
            client = self._client_for_specs()
            return client.simple_chat(
                prompt.strip(),
                system=system,
                max_tokens=1800,
            ).strip()
        except Exception as exc:
            return self._fallback_spec(description, requester, source, exc)

    def _client_for_specs(self) -> OpenAICompatibleClient:
        provider = os.getenv("APP_REQUEST_PROVIDER") or os.getenv("AI_PROVIDER", "deepseek")
        model = os.getenv("APP_REQUEST_MODEL")
        return OpenAICompatibleClient(provider=provider, model=model)

    def _fallback_spec(
        self,
        description: str,
        requester: str,
        source: str,
        error: Exception,
    ) -> str:
        return f"""# Summary
{description}

# Target Users
- Community members.

# MVP Scope
- Clarify the request.
- Build the smallest useful version.
- Share a preview before production release.

# Key Screens or Commands
- To be defined.

# Data and Integrations
- To be defined.

# Acceptance Criteria
- The requested workflow can be completed end to end.
- A maintainer can review the output before launch.

# Open Questions
- What platform should this run on?
- Who can approve production deployment?
- What data or APIs are required?

# Suggested Build Plan
1. Confirm scope with {requester}.
2. Create a GitHub issue from this spec.
3. Build in a branch or preview environment.
4. Ask for review before merge/deploy.

Spec generation note: model call failed for source {source}: {error}
"""

    def _write(self, request: AppRequest) -> None:
        json_path = self.requests_dir / f"{request.request_id}.json"
        md_path = self.requests_dir / f"{request.request_id}.md"

        json_path.write_text(json.dumps(asdict(request), indent=2) + "\n")
        md_path.write_text(self._markdown(request))

    def _markdown(self, request: AppRequest) -> str:
        metadata = json.dumps(request.metadata, indent=2)
        return f"""# {request.title}

- Request ID: `{request.request_id}`
- Requester: `{request.requester}`
- Source: `{request.source}`
- Created: `{request.created_at}`

## Original Request

{request.description}

## Generated Spec

{request.spec}

## Metadata

```json
{metadata}
```
"""

    def _maybe_autobuild(self, request: AppRequest) -> None:
        if os.getenv("APP_REQUEST_AUTOBUILD", "").lower() not in {"1", "true", "yes"}:
            return

        command = os.getenv("APP_REQUEST_BUILD_COMMAND")
        if not command:
            return

        md_path = self.requests_dir / f"{request.request_id}.md"
        env = os.environ.copy()
        env.update(
            {
                "APP_REQUEST_ID": request.request_id,
                "APP_REQUEST_MARKDOWN_PATH": str(md_path),
                "APP_REQUEST_TITLE": request.title,
            }
        )
        subprocess.Popen(command, shell=True, env=env)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Create an app request artifact.")
    parser.add_argument("description", help="Community app request")
    parser.add_argument("--requester", default="local")
    parser.add_argument("--source", default="cli")
    parser.add_argument("--workspace", default=os.getenv("WORKSPACE_PATH", "./workspace"))
    args = parser.parse_args()

    store = AppRequestStore(args.workspace)
    request = store.create(args.description, args.requester, args.source)
    print(request.request_id)
    print(store.requests_dir / f"{request.request_id}.md")


if __name__ == "__main__":
    main()
