import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import OnboardingChecklistCard from "../src/components/onboarding-checklist-card";

const steps = [
  {
    step_id: "s1",
    title: "Create App",
    description: "Register your first app",
    required: true,
    completed: true,
  },
  {
    step_id: "s2",
    title: "Add Webhook",
    description: "Set up webhook",
    required: true,
    completed: false,
  },
  {
    step_id: "s3",
    title: "Invite Team",
    description: "Add teammates",
    required: false,
    completed: false,
  },
];

describe("OnboardingChecklistCard", () => {
  it("renders header and percentage", () => {
    const { container } = render(
      <OnboardingChecklistCard steps={steps} completionPct={50} appName="App" />,
    );
    expect(container.textContent).toContain("Onboarding");
    expect(container.textContent).toContain("50%");
  });

  it("shows step count", () => {
    const { container } = render(
      <OnboardingChecklistCard steps={steps} completionPct={33} appName="App" />,
    );
    expect(container.textContent).toContain("1/3 steps completed");
  });

  it("shows step titles", () => {
    const { container } = render(
      <OnboardingChecklistCard steps={steps} completionPct={33} appName="App" />,
    );
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("Add Webhook");
  });

  it("shows optional label", () => {
    const { container } = render(
      <OnboardingChecklistCard steps={steps} completionPct={33} appName="App" />,
    );
    expect(container.textContent).toContain("optional");
  });
});
