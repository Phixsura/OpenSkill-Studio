import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IntegrationWizardSteps } from "@/components/integration-wizard-steps";

describe("IntegrationWizardSteps", () => {
  it("renders wizard", () => {
    const onNext = vi.fn();
    const { container, getByText } = render(
      <IntegrationWizardSteps name="Slack" icon="💬" progressPct={50} currentStep={2}
        onNext={onNext} onBack={vi.fn()}
        steps={[
          { index: 0, title: "Authorize", status: "completed" },
          { index: 1, title: "Select Channel", status: "completed" },
          { index: 2, title: "Configure", status: "current" },
          { index: 3, title: "Test", status: "pending" },
        ]} />
    );
    expect(container.textContent).toContain("Connect Slack");
    expect(container.textContent).toContain("Authorize");
    expect(container.textContent).toContain("Configure");
    fireEvent.click(getByText("Next"));
    expect(onNext).toHaveBeenCalled();
  });
});
