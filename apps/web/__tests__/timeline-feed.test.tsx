import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimelineFeed } from "@/components/timeline-feed";

describe("TimelineFeed", () => {
  const items = [
    { id: "1", title: "Published v2.0", description: "Major release", icon: "🚀", timestamp: "2026-01-02T00:00:00Z", actor: "Alice", type: "release" },
    { id: "2", title: "Created", description: "", icon: "✨", timestamp: "2026-01-01T00:00:00Z", actor: "Bob", type: "create" },
  ];
  it("renders items", () => {
    const { container } = render(<TimelineFeed items={items} />);
    expect(container.textContent).toContain("Published v2.0");
    expect(container.textContent).toContain("Major release");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("Created");
  });
  it("shows icons", () => {
    const { container } = render(<TimelineFeed items={items} />);
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("✨");
  });
});
