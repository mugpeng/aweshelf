"""aweswitch profile commands."""

import json

import click

from aweshelf.lib.aweswitch import load_aweswitch_config


def list_profiles(config: dict | None = None, provider: str | None = None) -> list[dict]:
    config = config if config is not None else load_aweswitch_config()
    if not config:
        return []
    result = []
    profiles_by_provider = config.get("profiles", {})
    for profile_provider in sorted(profiles_by_provider):
        if provider and profile_provider != provider:
            continue
        profiles = profiles_by_provider.get(profile_provider, {})
        if not isinstance(profiles, dict):
            continue
        for name in sorted(profiles):
            result.append({"provider": profile_provider, "name": name})
    return result


def format_profiles_json(profiles: list[dict]) -> str:
    return json.dumps(profiles, indent=2, ensure_ascii=False)


def format_profiles_table(profiles: list[dict]) -> str:
    if not profiles:
        return "No aweswitch profiles found."
    headers = ["PROVIDER", "PROFILE"]
    rows = [[p["provider"], p["name"]] for p in profiles]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = [
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "  ".join("-" * width for width in widths),
    ]
    for row in rows:
        lines.append("  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
    return "\n".join(lines)


@click.command("profiles")
@click.option("-p", "--provider", default=None, help="Filter by provider.")
@click.option("--json", "as_json", is_flag=True, help="Output as raw JSON.")
def profiles_command(provider, as_json):
    """List aweswitch profiles."""
    profiles = list_profiles(provider=provider)
    click.echo(format_profiles_json(profiles) if as_json else format_profiles_table(profiles))
