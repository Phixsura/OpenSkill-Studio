import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingWizard } from "@/components/onboarding-wizard";

describe("OnboardingWizard", () => {
  it("renders wizard", () => {
    const onComplete = vi.fn();
    const { container, getAllByText } = render(
      <OnboardingWizard progressPct={17} completedCount={1} total={6} onComplete={onComplete}
        steps={[
          { id: "profile", title: "Complete Profile", description: "Set name", completed: true, index: 0 },
          { id: "create_app", title: "Create App", description: "Register app", completed: false, index: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Get Started");
    expect(container.textContent).toContain("1/6");
    expect(container.textContent).toContain("17%");
    expect(container.textContent).toContain("Complete Profile");
    expect(container.textContent).toContain("Create App");
    fireEvent.click(getAllByText("Start")[0]);
    expect(onComplete).toHaveBeenCalledWith("create_app");
  });
});
