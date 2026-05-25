"""Resume command."""

import os

import click

from aweshelf.lib.store import find_bookmark
from aweshelf.lib.aweswitch import profile_exists, build_resume_command


@click.command("resume")
@click.argument("bookmark_id")
@click.option("--profile", default=None, help="Override aweswitch profile.")
@click.option("--raw", is_flag=True, help="Skip aweswitch, use claude/codex directly.")
def resume_command(bookmark_id, profile, raw):
    """Resume a bookmarked session."""
    b = find_bookmark(bookmark_id)
    if b is None:
        raise click.ClickException(f"bookmark not found: {bookmark_id}")

    use_profile = profile or b.aweswitch_profile

    if use_profile and not raw:
        if not profile_exists(use_profile):
            click.echo(f"Warning: aweswitch profile '{use_profile}' not found.", err=True)
            click.echo("Use --raw to skip aweswitch, or --profile to specify a different profile.", err=True)
            raise SystemExit(1)

    cmd = build_resume_command(b.provider, use_profile, b.session_id, raw=raw)
    click.echo(f"Resuming {b.id} — {b.title}")
    click.echo(f"  $ {' '.join(cmd)}")

    try:
        os.execvpe(cmd[0], cmd, os.environ)
    except FileNotFoundError:
        raise click.ClickException(f"command not found: {cmd[0]}")
    except OSError as exc:
        raise click.ClickException(f"failed to run {cmd[0]}: {exc}")
