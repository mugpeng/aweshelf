"""Browse command — TUI entry point."""

import os
import sys

import click

from aweshelf.lib.aweswitch import profile_exists, build_resume_command


@click.command("browse")
def browse_command():
    """Browse bookmarks interactively."""
    try:
        from aweshelf.tui.app import BookmarkBrowser
    except ImportError:
        raise click.ClickException("textual is required for browse. Install with: pip install textual")

    app = BookmarkBrowser()
    result = app.run()

    if result is not None:
        b = result
        use_profile = b.aweswitch_profile
        if use_profile and profile_exists(use_profile):
            cmd = build_resume_command(b.provider, use_profile, b.session_id)
        else:
            cmd = build_resume_command(b.provider, None, b.session_id, raw=True)

        click.echo(f"Resuming {b.id} — {b.title}")
        click.echo(f"  $ {' '.join(cmd)}")
        try:
            os.execvpe(cmd[0], cmd, os.environ)
        except FileNotFoundError:
            raise click.ClickException(f"command not found: {cmd[0]}")
        except OSError as exc:
            raise click.ClickException(f"failed to run {cmd[0]}: {exc}")
