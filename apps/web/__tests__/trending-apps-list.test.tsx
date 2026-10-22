import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrendingAppsList } from "@/components/trending-apps-list";

const APPS = [
  { name: "Hot App", category: "connector", recentInstalls: 50, trendingScore: 200 },
  { name: "Rising", category: "automation", recentInstalls: 20, trendingScore: 100 },
];

describe("TrendingAppsList", () => {
  it("shows ranked apps", () => {
    const { container } = render(<TrendingAppsList apps={APPS} />);
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("Hot App");
  });
  it("shows scores", () => {
    const { container } = render(<TrendingAppsList apps={APPS} />);
    expect(container.textContent).toContain("200");
  });
  it("empty state", () => {
    const { container } = render(<TrendingAppsList apps={[]} />);
    expect(container.textContent).toContain("No trending");
  });
});
