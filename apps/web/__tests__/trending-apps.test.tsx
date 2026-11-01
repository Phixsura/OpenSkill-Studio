import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrendingApps } from "@/components/trending-apps";

describe("TrendingApps", () => {
  const apps = [
    { id: "a1", name: "FastApp", icon: "🚀", category: "tools", growthPct: 400, velocity: 71.4, rating: 4.5 },
  ];
  it("renders trending", () => {
    const { container } = render(<TrendingApps apps={apps} period="7d" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Trending");
    expect(container.textContent).toContain("FastApp");
    expect(container.textContent).toContain("400%");
    expect(container.textContent).toContain("#1");
  });
});
