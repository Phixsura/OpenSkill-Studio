import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiConsumerOnboardingMilestoneCard from "../src/components/api-developer-platform-sdk-api-consumer-onboarding-milestone-card";

const consumers = [
  { consumer_id: "acme", completed_count: 6, completion_pct: 100, next_milestone: null, fully_onboarded: true },
  { consumer_id: "beta", completed_count: 2, completion_pct: 33.3, next_milestone: "first_api_call", fully_onboarded: false },
];

describe("Card", () => {
  it("shows milestones", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerOnboardingMilestoneCard consumers={consumers} completionRate={50} fullyOnboardedCount={1} appName="App" />);
    expect(container.textContent).toContain("Onboarding Milestones");
    expect(container.textContent).toContain("1 complete");
    expect(container.textContent).toContain("50% rate");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("first api call");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerOnboardingMilestoneCard consumers={[]} completionRate={0} fullyOnboardedCount={0} appName="App" />);
    expect(container.textContent).toContain("No milestone data");
  });
});
