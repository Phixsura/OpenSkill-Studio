import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIOnboardingFunnelCard from "../src/components/api-developer-api-onboarding-funnel-card";

const stages = [
  { stage_name: "Sign Up", entered: 1000, completed: 800, conversion_rate: 80 },
  { stage_name: "Create App", entered: 800, completed: 500, conversion_rate: 62.5 },
  { stage_name: "First API Call", entered: 500, completed: 300, conversion_rate: 60 },
];

describe("APIDeveloperAPIOnboardingFunnelCard", () => {
  it("shows funnel", () => {
    const { container } = render(<APIDeveloperAPIOnboardingFunnelCard stages={stages} overallConversion={30} appName="App" />);
    expect(container.textContent).toContain("Onboarding Funnel");
    expect(container.textContent).toContain("30% overall");
    expect(container.textContent).toContain("Sign Up");
    expect(container.textContent).toContain("800/1000");
    expect(container.textContent).toContain("First API Call");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIOnboardingFunnelCard stages={[]} overallConversion={0} appName="App" />);
    expect(container.textContent).toContain("No funnel data");
  });
});
