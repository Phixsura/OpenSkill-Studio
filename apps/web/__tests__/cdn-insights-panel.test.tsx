import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CdnInsightsPanel } from "@/components/cdn-insights-panel";

describe("CdnInsightsPanel", () => {
  it("renders insights", () => {
    const { container } = render(
      <CdnInsightsPanel totalAssets={50} cached={40} hitRatio={80}
        bandwidthSavedPct={65} byType={{ script: 20, style: 10, image: 20 }}
        suggestions={[{ asset: "/big.js", action: "cache", reason: "Large uncached" }]} />
    );
    expect(container.textContent).toContain("CDN Insights");
    expect(container.textContent).toContain("50 assets");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("/big.js");
    expect(container.textContent).toContain("Large uncached");
  });
});
