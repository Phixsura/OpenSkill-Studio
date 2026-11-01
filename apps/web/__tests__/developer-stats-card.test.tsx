import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperStatsCard } from "@/components/developer-stats-card";

describe("DeveloperStatsCard", () => {
  it("shows all stats", () => {
    const { container } = render(<DeveloperStatsCard appCount={10} publishedCount={6} totalInstalls={200} avgHealthScore={95} />);
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("95%");
  });

  it("shows healthy icon for good health", () => {
    const { container } = render(<DeveloperStatsCard appCount={1} publishedCount={1} totalInstalls={0} avgHealthScore={90} />);
    expect(container.textContent).toContain("💚");
  });

  it("shows warning for low health", () => {
    const { container } = render(<DeveloperStatsCard appCount={1} publishedCount={1} totalInstalls={0} avgHealthScore={50} />);
    expect(container.textContent).toContain("⚠️");
  });

  it("renders 4 cards", () => {
    const { container } = render(<DeveloperStatsCard appCount={0} publishedCount={0} totalInstalls={0} avgHealthScore={100} />);
    expect(container.querySelectorAll("[class*='rounded-lg']").length).toBe(4);
  });
});
