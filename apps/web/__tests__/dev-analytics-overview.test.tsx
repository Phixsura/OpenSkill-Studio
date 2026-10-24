import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevAnalyticsOverview } from "@/components/dev-analytics-overview";

describe("DevAnalyticsOverview", () => {
  it("renders overview", () => {
    const { container } = render(
      <DevAnalyticsOverview appCount={5} installsDisplay="80,000" apiDisplay="1,500,000"
        revenueDisplay="$7,000" avgRating={4.2} period="30d"
        topApp={{ name: "App A", installs: 50000 }}
        growthAreas={["1 app below 4.0"]} />
    );
    expect(container.textContent).toContain("Developer Analytics");
    expect(container.textContent).toContain("80,000");
    expect(container.textContent).toContain("$7,000");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("1 app below 4.0");
  });
});
