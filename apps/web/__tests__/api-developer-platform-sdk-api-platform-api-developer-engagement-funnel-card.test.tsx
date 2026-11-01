import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnelCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-engagement-funnel-card";

const stages = [
  { stage: "visited_docs", count: 1000 },
  { stage: "created_account", count: 500 },
  { stage: "power_user", count: 50 },
];

describe("Card", () => {
  it("shows funnel", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnelCard stages={stages} conversionRate={5} biggestDropoff="created_account" appName="App" />);
    expect(container.textContent).toContain("Engagement Funnel");
    expect(container.textContent).toContain("5% end-to-end");
    expect(container.textContent).toContain("visited docs");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("Biggest drop-off: created account");
  });
});
