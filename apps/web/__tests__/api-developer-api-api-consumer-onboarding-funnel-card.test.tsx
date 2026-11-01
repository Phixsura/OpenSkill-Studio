import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiConsumerOnboardingFunnelCard from "../src/components/api-developer-api-api-consumer-onboarding-funnel-card";

const steps = [
  { step: "signup", entered: 100, completed: 100, conversion_rate: 100 },
  { step: "api_key_created", entered: 80, completed: 75, conversion_rate: 93.8 },
  { step: "first_request", entered: 60, completed: 50, conversion_rate: 83.3 },
];

describe("APIDeveloperAPIApiConsumerOnboardingFunnelCard", () => {
  it("shows funnel", () => {
    const { container } = render(<APIDeveloperAPIApiConsumerOnboardingFunnelCard steps={steps} overallConversion={25} appName="App" />);
    expect(container.textContent).toContain("Onboarding Funnel");
    expect(container.textContent).toContain("25% end-to-end");
    expect(container.textContent).toContain("signup");
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("api key created");
  });
});
