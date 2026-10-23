import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrendingAppsList } from "@/components/trending-apps-list";

describe("TrendingAppsList", () => {
  it("renders trending", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <TrendingAppsList onSelect={onSelect} apps={[
        { name: "Hot App", icon: "🔥", rating: 4.8, recentInstalls: 5000, trendingScore: 42.5, rank: 1 },
        { name: "Medium App", icon: "📱", rating: 4.2, recentInstalls: 500, trendingScore: 28.1, rank: 2 },
      ]} />
    );
    expect(container.textContent).toContain("Trending Apps");
    expect(container.textContent).toContain("Hot App");
    expect(container.textContent).toContain("4.8");
    expect(container.textContent).toContain("5,000");
    fireEvent.click(getByText("Hot App"));
    expect(onSelect).toHaveBeenCalledWith("Hot App");
  });
});
