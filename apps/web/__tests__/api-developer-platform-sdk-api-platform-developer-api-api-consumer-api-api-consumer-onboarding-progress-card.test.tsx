import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-onboarding-progress-card";

describe("ConsumerOnboardingProgressCard", () => {
  it("shows progress", () => {
    const phases = [{ phase_id: "p1", name: "Register", completed: true, required: true }, { phase_id: "p2", name: "Test", completed: false, required: false }];
    const { container } = render(<Card consumerId="c1" phases={phases} completionPct={50} currentPhase="Test" ready={false} appName="App" />);
    expect(container.textContent).toContain("Onboarding Progress");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Register");
    expect(container.textContent).toContain("(optional)");
  });
  it("shows ready", () => {
    const { container } = render(<Card consumerId="c1" phases={[]} completionPct={100} currentPhase="complete" ready={true} appName="App" />);
    expect(container.textContent).toContain("Ready");
  });
});
