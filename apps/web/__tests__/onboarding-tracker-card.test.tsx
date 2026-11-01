import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import OnboardingTrackerCard from "../src/components/onboarding-tracker-card";

const steps = [
  { step_id: "profile", name: "Complete Profile", completed: true, required: true },
  { step_id: "connect", name: "Connect Account", completed: false, required: true },
  { step_id: "tour", name: "Take Tour", completed: false, required: false },
];

describe("OnboardingTrackerCard", () => {
  it("renders header with user id", () => {
    const { container } = render(
      <OnboardingTrackerCard
        steps={steps}
        completionPct={33}
        isComplete={false}
        userId="user-42"
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Onboarding");
    expect(container.textContent).toContain("user-42");
  });

  it("shows completion percentage", () => {
    const { container } = render(
      <OnboardingTrackerCard
        steps={steps}
        completionPct={33}
        isComplete={false}
        userId="u1"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("33%");
  });

  it("shows complete badge", () => {
    const { container } = render(
      <OnboardingTrackerCard
        steps={steps}
        completionPct={100}
        isComplete={true}
        userId="u1"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Complete");
  });

  it("renders step names", () => {
    const { container } = render(
      <OnboardingTrackerCard
        steps={steps}
        completionPct={33}
        isComplete={false}
        userId="u1"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Complete Profile");
    expect(container.textContent).toContain("Connect Account");
    expect(container.textContent).toContain("Take Tour");
  });

  it("shows optional label", () => {
    const { container } = render(
      <OnboardingTrackerCard
        steps={steps}
        completionPct={33}
        isComplete={false}
        userId="u1"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("optional");
  });

  it("shows check marks for completed", () => {
    const { container } = render(
      <OnboardingTrackerCard
        steps={steps}
        completionPct={33}
        isComplete={false}
        userId="u1"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("○");
  });
});
