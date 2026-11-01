import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingProgressWidget } from "@/components/onboarding-progress-widget";

describe("OnboardingProgressWidget", () => {
  it("renders progress", () => {
    const onStart = vi.fn();
    const { container, getAllByText } = render(
      <OnboardingProgressWidget progressPct={50} completedCount={3} totalSteps={7}
        message="💪 Halfway done!" onStart={onStart}
        steps={[
          { id: "profile", title: "Complete Profile", completed: true },
          { id: "first_app", title: "Create App", completed: true },
          { id: "api_key", title: "Generate Key", completed: true },
          { id: "first_call", title: "First API Call", completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Halfway done");
    expect(container.textContent).toContain("3/7");
    fireEvent.click(getAllByText("Start")[0]);
    expect(onStart).toHaveBeenCalledWith("first_call");
  });
});
