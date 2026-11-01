import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import OnboardingTrackerCard from "../src/components/api-developer-platform-sdk-consumer-api-onboarding-tracker-card";

describe("OnboardingTrackerCard", () => {
  it("renders title and steps", () => {
    const { container } = render(<OnboardingTrackerCard />);
    expect(container.textContent).toContain("Onboarding Tracker");
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("Make First Call");
  });

  it("shows progress", () => {
    const { container } = render(<OnboardingTrackerCard />);
    expect(container.textContent).toContain("50% complete");
    expect(container.textContent).toContain("2/4");
  });
});
