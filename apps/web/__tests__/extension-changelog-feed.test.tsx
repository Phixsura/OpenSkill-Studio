import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionChangelogFeed } from "@/components/extension-changelog-feed";

const mockEntries = [
  { version: "2.0.0", title: "Complete Redesign", description: "New UI and API", publishedAt: "Oct 25", author: "alice", type: "major" as const },
  { version: "1.1.0", title: "Search Feature", description: "Added full-text search", publishedAt: "Oct 15", author: "bob", type: "minor" as const },
  { version: "1.0.1", title: "Bug Fix", description: "Fixed login crash", publishedAt: "Oct 5", author: "alice", type: "patch" as const },
];

describe("ExtensionChangelogFeed", () => {
  it("renders entries with versions", () => {
    const { container } = render(
      <ExtensionChangelogFeed extensionName="Slack Bot" entries={mockEntries} />
    );
    expect(container.textContent).toContain("Slack Bot Updates");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Complete Redesign");
    expect(container.textContent).toContain("v1.0.1");
  });

  it("shows type badges", () => {
    const { container } = render(
      <ExtensionChangelogFeed extensionName="Test" entries={mockEntries} />
    );
    expect(container.textContent).toContain("Major");
    expect(container.textContent).toContain("Minor");
    expect(container.textContent).toContain("Patch");
  });

  it("shows RSS link", () => {
    const { container } = render(
      <ExtensionChangelogFeed extensionName="Test" entries={mockEntries} rssUrl="https://feed.xml" />
    );
    expect(container.textContent).toContain("RSS Feed");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ExtensionChangelogFeed extensionName="Test" entries={[]} />
    );
    expect(container.textContent).toContain("No updates");
  });
});
