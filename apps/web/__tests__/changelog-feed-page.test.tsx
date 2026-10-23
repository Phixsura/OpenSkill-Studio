import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogFeedPage } from "@/components/changelog-feed-page";

describe("ChangelogFeedPage", () => {
  const entries = [
    { appName: "AppB", appIcon: "📦", version: "1.5", title: "Bug fix", type: "fixed", date: "2026-03-02" },
  ];
  it("renders feed", () => {
    const { container } = render(<ChangelogFeedPage entries={entries} total={1} appsWithUpdates={1} />);
    expect(container.textContent).toContain("What's New");
    expect(container.textContent).toContain("AppB");
    expect(container.textContent).toContain("Bug fix");
    expect(container.textContent).toContain("v1.5");
  });
});
