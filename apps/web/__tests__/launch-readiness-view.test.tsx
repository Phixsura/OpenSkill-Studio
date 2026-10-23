import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LaunchReadinessView } from "@/components/launch-readiness-view";

describe("LaunchReadinessView", () => {
  const items = [
    { id: "branding", label: "Icon ready", category: "design", completed: true },
    { id: "testing", label: "QA complete", category: "engineering", completed: false },
  ];
  const cats = [{ category: "design", total: 1, done: 1, pct: 100 },
                { category: "engineering", total: 1, done: 0, pct: 0 }];
  it("renders", () => {
    const { container } = render(
      <LaunchReadinessView items={items} readinessPct={50} launchReady={false}
        categories={cats} onToggle={vi.fn()} onLaunch={vi.fn()} />
    );
    expect(container.textContent).toContain("Launch Readiness");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⬜");
    expect(container.textContent).toContain("Complete 1 remaining");
  });
});
