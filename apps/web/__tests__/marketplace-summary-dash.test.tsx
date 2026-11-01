import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceSummaryDash } from "@/components/marketplace-summary-dash";

describe("MarketplaceSummaryDash", () => {
  it("renders summary", () => {
    const { container } = render(
      <MarketplaceSummaryDash totalApps={500} totalDevs={200} avgRating={4.3}
        uptimePct={99.99} newApps30d={35} devSatisfaction={92}
        categories={[
          { name: "Communication", icon: "💬", apps: 85 },
          { name: "Tools", icon: "🛠️", apps: 72 },
        ]} />
    );
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("4.3");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("Communication (85)");
    expect(container.textContent).toContain("+35 new apps");
    expect(container.textContent).toContain("92%");
  });
});
