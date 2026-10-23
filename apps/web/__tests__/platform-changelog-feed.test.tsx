import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformChangelogFeed } from "@/components/platform-changelog-feed";

describe("PlatformChangelogFeed", () => {
  it("renders feed", () => {
    const { container } = render(
      <PlatformChangelogFeed total={3} byType={{ feat: 2, fix: 1 }}
        entries={[
          { service: "API", type: "feat", title: "New endpoint", date: "2026-10-24", version: "3.2" },
          { service: "Dashboard", type: "feat", title: "Dark mode", date: "2026-10-24", version: "2.0" },
          { service: "API", type: "fix", title: "Auth bug", date: "2026-10-23", version: "3.1.1" },
        ]} />
    );
    expect(container.textContent).toContain("Platform Changelog");
    expect(container.textContent).toContain("New endpoint");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("3 changes total");
    expect(container.textContent).toContain("feat: 2");
  });
});
