import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogRSSCard from "../src/components/changelog-rss-card";

const feed = {
  title: "My App Changelog",
  link: "https://example.com/changelog.xml",
  language: "en",
  item_count: 15,
  latest_items: [
    { title: "Major update", version: "2.0.0", date: "2026-10-28" },
    { title: "Bug fixes", version: "1.9.1", date: "2026-10-15" },
  ],
};

describe("ChangelogRSSCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ChangelogRSSCard feed={feed} appName="My App" />);
    expect(container.textContent).toContain("RSS Feed");
    expect(container.textContent).toContain("My App");
  });

  it("shows RSS badge and item count", () => {
    const { container } = render(<ChangelogRSSCard feed={feed} appName="App" />);
    expect(container.textContent).toContain("RSS 2.0");
    expect(container.textContent).toContain("15 items");
  });

  it("shows feed title and link", () => {
    const { container } = render(<ChangelogRSSCard feed={feed} appName="App" />);
    expect(container.textContent).toContain("My App Changelog");
    expect(container.textContent).toContain("https://example.com/changelog.xml");
  });

  it("renders latest items", () => {
    const { container } = render(<ChangelogRSSCard feed={feed} appName="App" />);
    expect(container.textContent).toContain("Major update");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("2026-10-28");
  });

  it("shows empty state", () => {
    const emptyFeed = { ...feed, latest_items: [], item_count: 0 };
    const { container } = render(<ChangelogRSSCard feed={emptyFeed} appName="App" />);
    expect(container.textContent).toContain("No items published");
  });
});
