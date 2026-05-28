export interface AweshelfBookmark {
  id: string;
  provider: string;
  session_id: string;
  title: string;
  category: string;
  project_path: string;
  first_prompt?: string;
  aweswitch_profile?: string | null;
  bookmarked_at: string;
}

export interface BookmarkGroup {
  category: string;
  bookmarks: AweshelfBookmark[];
}

export type BookmarkSortBy = "title" | "recent" | "id";

export interface BookmarkViewOptions {
  sortBy?: BookmarkSortBy;
  provider?: string;
  category?: string;
}

export const UNCATEGORIZED_CATEGORY = "Uncategorized";

export function normalizeCategory(category: string | undefined | null): string {
  const trimmed = category?.trim();
  return trimmed ? trimmed : UNCATEGORIZED_CATEGORY;
}

export function filterBookmarks(
  bookmarks: AweshelfBookmark[],
  options: BookmarkViewOptions = {}
): AweshelfBookmark[] {
  return bookmarks.filter((bookmark) => {
    if (options.provider && bookmark.provider !== options.provider) {
      return false;
    }
    if (options.category && normalizeCategory(bookmark.category) !== options.category) {
      return false;
    }
    return true;
  });
}

export function groupBookmarks(
  bookmarks: AweshelfBookmark[],
  options: BookmarkViewOptions = {}
): BookmarkGroup[] {
  const grouped = new Map<string, AweshelfBookmark[]>();

  for (const bookmark of filterBookmarks(bookmarks, options)) {
    const category = normalizeCategory(bookmark.category);
    const current = grouped.get(category) ?? [];
    current.push(bookmark);
    grouped.set(category, current);
  }

  return [...grouped.entries()]
    .sort(([left], [right]) => compareCategories(left, right))
    .map(([category, categoryBookmarks]) => ({
      category,
      bookmarks: [...categoryBookmarks].sort((left, right) =>
        compareBookmarks(left, right, options.sortBy ?? "title")
      )
    }));
}

function compareCategories(left: string, right: string): number {
  if (left === UNCATEGORIZED_CATEGORY && right !== UNCATEGORIZED_CATEGORY) {
    return 1;
  }
  if (right === UNCATEGORIZED_CATEGORY && left !== UNCATEGORIZED_CATEGORY) {
    return -1;
  }
  return left.localeCompare(right);
}

function compareBookmarks(
  left: AweshelfBookmark,
  right: AweshelfBookmark,
  sortBy: BookmarkSortBy
): number {
  if (sortBy === "recent") {
    const byDate = right.bookmarked_at.localeCompare(left.bookmarked_at);
    if (byDate !== 0) {
      return byDate;
    }
  }

  if (sortBy === "id") {
    return left.id.localeCompare(right.id);
  }

  if (sortBy === "title" || sortBy === "recent") {
    const byTitle = left.title.localeCompare(right.title);
    if (byTitle !== 0) {
      return byTitle;
    }
  }
  return left.id.localeCompare(right.id);
}
