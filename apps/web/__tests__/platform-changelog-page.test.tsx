import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformChangelogPage } from "@/components/platform-changelog-page";

describe("PlatformChangelogPage", () => {
  it("renders", () => {
    const entries = [
      { title: "App1 v2.0", date: "2026-10-01", type: "app_update", link: "/app1" },
      { title: "API v3", date: "2026-10-15", type: "platform", link: "/changelog" },
    ];
    const { container } = render(<PlatformChangelogPage entries={entries} rssUrl="/feed.rss" />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("App1 v2.0");
    expect(container.textContent).toContain("API v3");
    expect(container.textContent).toContain("RSS");
  });
});
