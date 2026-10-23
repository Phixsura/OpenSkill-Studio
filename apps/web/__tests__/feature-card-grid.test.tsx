import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureCardGrid } from "@/components/feature-card-grid";

describe("FeatureCardGrid", () => {
  const cards = [
    { title: "Easy SDK", description: "Get started fast", icon: "🚀", category: "dev", link: null },
    { title: "Real-time", description: "Live updates", icon: "⚡", category: "infra", link: null },
  ];
  it("renders", () => {
    const { container } = render(<FeatureCardGrid cards={cards} />);
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("Easy SDK");
    expect(container.textContent).toContain("Get started fast");
    expect(container.textContent).toContain("⚡");
    expect(container.textContent).toContain("Real-time");
  });
});
