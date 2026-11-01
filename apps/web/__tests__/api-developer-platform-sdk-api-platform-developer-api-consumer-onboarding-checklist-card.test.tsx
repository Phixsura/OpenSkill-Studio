import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-onboarding-checklist-card";

const steps = [
  { step_id: "s1", title: "Create API key", completed: true, required: true },
  { step_id: "s2", title: "Read docs", completed: false, required: false },
];

describe("OnboardingChecklistCard", () => {
  it("shows checklist", () => {
    const { container } = render(<Card consumerId="c1" steps={steps} progressPct={50} onboarded={false} appName="App" />);
    expect(container.textContent).toContain("Onboarding");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Create API key");
    expect(container.textContent).toContain("Read docs");
    expect(container.textContent).toContain("(optional)");
  });
  it("shows complete", () => {
    const { container } = render(<Card consumerId="c1" steps={steps} progressPct={100} onboarded={true} appName="App" />);
    expect(container.textContent).toContain("Complete");
  });
});
