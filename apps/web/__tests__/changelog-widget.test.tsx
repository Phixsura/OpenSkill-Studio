import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogWidget } from "@/components/changelog-widget";

describe("ChangelogWidget", () => {
  const entries = [{ version: "2.1.0", title: "Dark mode", type: "added", icon: "✨", date: "2026-10-20" }];
  it("renders widget", () => {
    const { container } = render(
      <ChangelogWidget appName="SuperApp" entries={entries} hasMore={true} onViewAll={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp Updates");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("View all updates");
  });
});
