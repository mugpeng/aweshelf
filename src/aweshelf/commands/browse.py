"""Browse command — TUI entry point."""

import click

from aweshelf.lib.resume import build_resume_target, format_resume_target, run_resume_target


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
        target = build_resume_target(result)

        if target.warning:
            click.echo(f"Warning: {target.warning}", err=True)
        click.echo(f"Resuming {result.id} — {result.title}")
        click.echo(f"  $ {format_resume_target(target)}")
        try:
            run_resume_target(target)
        except FileNotFoundError:
            raise click.ClickException(f"command not found: {target.argv[0]}")
        except OSError as exc:
            raise click.ClickException(f"failed to run {target.argv[0]}: {exc}")
