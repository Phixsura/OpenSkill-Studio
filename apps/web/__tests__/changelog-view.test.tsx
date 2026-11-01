import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogView } from "@/components/changelog-view";

describe("ChangelogView", () => {
  const releases = [
    { version: "2.0.0", date: "2026-01-15", has_breaking: true, entries: [
      { type: "breaking", icon: "💥", message: "Removed legacy API", breaking: true },
      { type: "feat", icon: "✨", message: "New dashboard", breaking: false },
    ]},
  ];
  it("renders release", () => {
    const { container } = render(<ChangelogView releases={releases} />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("Removed legacy API");
    expect(container.textContent).toContain("New dashboard");
    expect(container.textContent).toContain("💥");
  });
});
