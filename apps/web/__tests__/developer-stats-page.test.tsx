import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperStatsPage } from "@/components/developer-stats-page";

describe("DeveloperStatsPage", () => {
  it("renders stats", () => {
    const { container } = render(
      <DeveloperStatsPage developer="Alice" memberSince="2024-01-01"
        summary={{ totalApps: 5, installsDisplay: "105,000", totalReviews: 250, avgRating: 4.5, topApp: "SuperApp" }}
        badges={[{ id: "100k", label: "100K Club", icon: "🏆" }]} />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("105,000");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("100K Club");
  });
});
