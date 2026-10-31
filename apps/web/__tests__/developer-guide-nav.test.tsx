import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperGuideNav } from "@/components/developer-guide-nav";

describe("DeveloperGuideNav", () => {
  const sections = [
    { id: "quickstart", title: "Quickstart", icon: "🚀", estimatedMin: 5, completed: true, topicCount: 3, topics: [] },
    { id: "concepts", title: "Core Concepts", icon: "💡", estimatedMin: 15, completed: false, topicCount: 5, topics: [] },
  ];
  it("renders guide nav", () => {
    const { container } = render(
      <DeveloperGuideNav sections={sections} progressPct={50} totalReadingMin={80} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Developer Guide");
    expect(container.textContent).toContain("Quickstart");
    expect(container.textContent).toContain("Core Concepts");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("80 min");
  });
});
