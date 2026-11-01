import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogBookmarkCard from "../src/components/api-changelog-bookmark-card";

const bookmarks = [{ entry_id: "e1", title: "v2.0 Release", note: "Check migration guide" }];

describe("APIChangelogBookmarkCard", () => {
  it("shows bookmarks", () => {
    const { container } = render(<APIChangelogBookmarkCard bookmarks={bookmarks} appName="App" />);
    expect(container.textContent).toContain("Bookmarks");
    expect(container.textContent).toContain("v2.0 Release");
    expect(container.textContent).toContain("Check migration guide");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogBookmarkCard bookmarks={[]} appName="App" />);
    expect(container.textContent).toContain("No bookmarks");
  });
});
