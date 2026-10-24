import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryStatsChart } from "@/components/category-stats-chart";

const STATS = [
  { category: "connector", count: 15, installs: 500, avgHealth: 95 },
  { category: "automation", count: 10, installs: 300, avgHealth: 90 },
];

describe("CategoryStatsChart", () => {
  it("shows categories", () => {
    const { container } = render(<CategoryStatsChart stats={STATS} />);
    expect(container.textContent).toContain("connector");
    expect(container.textContent).toContain("automation");
  });

  it("shows counts", () => {
    const { container } = render(<CategoryStatsChart stats={STATS} />);
    expect(container.textContent).toContain("15 apps");
  });

  it("shows installs", () => {
    const { container } = render(<CategoryStatsChart stats={STATS} />);
    expect(container.textContent).toContain("500");
  });

  it("empty state", () => {
    const { container } = render(<CategoryStatsChart stats={[]} />);
    expect(container.textContent).toContain("No category data");
  });
});
