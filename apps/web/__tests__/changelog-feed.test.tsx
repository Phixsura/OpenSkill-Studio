import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogFeed } from "@/components/changelog-feed";

const ENTRIES = [
  { appName: "App A", version: "2.0", date: "2026-02", breaking: true },
  { appName: "App B", version: "1.1", date: "2026-03" },
];

describe("ChangelogFeed", () => {
  it("shows all entries", () => {
    const { container } = render(<ChangelogFeed entries={ENTRIES} />);
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("App B");
  });
  it("filters breaking only", () => {
    const { container } = render(<ChangelogFeed entries={ENTRIES} showBreakingOnly />);
    expect(container.textContent).toContain("App A");
    expect(container.textContent).not.toContain("App B");
  });
  it("empty state", () => {
    const { container } = render(<ChangelogFeed entries={[]} />);
    expect(container.textContent).toContain("No changelog");
  });
});
