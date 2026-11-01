import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-onboarding-wizard-card";

describe("OnboardingWizardCard", () => {
  it("shows wizard", () => {
    const steps = [{ step_id: "s1", title: "Create Key", completed: true, skippable: false, order: 1 }, { step_id: "s2", title: "Read Docs", completed: false, skippable: true, order: 2 }];
    const { container } = render(<Card consumerId="c1" steps={steps} progressPct={50} isComplete={false} appName="App" />);
    expect(container.textContent).toContain("Onboarding Wizard");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Create Key");
    expect(container.textContent).toContain("(optional)");
  });
  it("shows complete", () => {
    const { container } = render(<Card consumerId="c1" steps={[]} progressPct={100} isComplete={true} appName="App" />);
    expect(container.textContent).toContain("Done");
  });
});
