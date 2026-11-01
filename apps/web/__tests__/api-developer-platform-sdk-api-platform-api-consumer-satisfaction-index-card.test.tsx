import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndexCard from "../src/components/api-developer-platform-sdk-api-platform-api-consumer-satisfaction-index-card";

const indices = [{ consumer_id: "acme", csi: 92, satisfaction_tier: "delighted", api_reliability_score: 95, overall_nps: 80 }];

describe("Card", () => {
  it("shows satisfaction index", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndexCard indices={indices} avgCsi={85} dissatisfiedCount={2} appName="App" />);
    expect(container.textContent).toContain("Satisfaction Index");
    expect(container.textContent).toContain("avg CSI: 85");
    expect(container.textContent).toContain("2 dissatisfied");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("92");
    expect(container.textContent).toContain("delighted");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndexCard indices={[]} avgCsi={0} dissatisfiedCount={0} appName="App" />);
    expect(container.textContent).toContain("No satisfaction data");
  });
});
