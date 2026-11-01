import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKWebhookConsumerTrustScoreCard from "../src/components/api-developer-platform-sdk-webhook-consumer-trust-score-card";

const scores = [{ consumer_id: "acme", trust_score: 92, trust_tier: "trusted", violations: 0, days_active: 365 }];

describe("Card", () => {
  it("shows trust scores", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookConsumerTrustScoreCard scores={scores} restrictedCount={2} appName="App" />);
    expect(container.textContent).toContain("Trust Scores");
    expect(container.textContent).toContain("2 restricted");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("92");
    expect(container.textContent).toContain("trusted");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookConsumerTrustScoreCard scores={[]} restrictedCount={0} appName="App" />);
    expect(container.textContent).toContain("No trust data");
  });
});
