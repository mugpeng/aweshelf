import { AweshelfBookmark } from "./bookmark";

export function formatBookmarkDetailMarkdown(bookmark: AweshelfBookmark): string {
  const lines = [
    `# ${bookmark.title || bookmark.id}`,
    "",
    `- **ID:** \`${bookmark.id}\``,
    `- **Provider:** \`${bookmark.provider}\``,
    `- **Session ID:** \`${bookmark.session_id}\``,
    `- **Category:** \`${bookmark.category || "Uncategorized"}\``,
    `- **Project:** \`${bookmark.project_path || "-"}\``,
    `- **aweswitch profile:** \`${bookmark.aweswitch_profile || "-"}\``,
    `- **Bookmarked at:** \`${bookmark.bookmarked_at || "-"}\``
  ];

  if (bookmark.first_prompt) {
    lines.push("", "## First Prompt", "", bookmark.first_prompt);
  }

  return lines.join("\n");
}
