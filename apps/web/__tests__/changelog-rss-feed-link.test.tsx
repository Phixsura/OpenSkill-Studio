import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogRssFeedLink } from "@/components/changelog-rss-feed-link";

describe("ChangelogRssFeedLink", () => {
  it("renders", () => {
    const { container } = render(
      <ChangelogRssFeedLink appName="MyApp" appId="a1"
        feedUrl="https://marketplace.openskill.dev/apps/a1/changelog.rss" onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("MyApp Changelog Feed");
    expect(container.textContent).toContain("changelog.rss");
    expect(container.textContent).toContain("Subscribe");
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangelogRssFeedLink appName="App" appId="a1" feedUrl="https://x.com/feed" onCopy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy URL")!);
    expect(fn).toHaveBeenCalled();
  });
});
