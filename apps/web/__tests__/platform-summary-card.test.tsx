import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSummaryCard } from "@/components/platform-summary-card";

describe("PlatformSummaryCard", () => {
  it("renders summary", () => {
    const { container } = render(
      <PlatformSummaryCard apps={500} users={10000} displayRevenue="$50,000"
        uptime={99.95} growthPct={15} health="excellent"
        highlights={["25 new apps", "15% growth"]} />
    );
    expect(container.textContent).toContain("Platform Summary");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("$50,000");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("25 new apps");
  });
});
