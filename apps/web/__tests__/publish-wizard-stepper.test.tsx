import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublishWizardStepper } from "@/components/publish-wizard-stepper";

describe("PublishWizardStepper", () => {
  it("renders wizard", () => {
    const onPublish = vi.fn();
    const { container, getByText } = render(
      <PublishWizardStepper progressPct={80} currentStep="submit" readyToSubmit={true}
        onStep={vi.fn()} onPublish={onPublish}
        steps={[
          { id: "listing", title: "Listing", description: "Complete listing", completed: true },
          { id: "submit", title: "Submit", description: "Submit for review", completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Publish to Marketplace");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("Listing");
    expect(container.textContent).toContain("Submit for Review");
    fireEvent.click(getByText("🚀 Submit for Review"));
    expect(onPublish).toHaveBeenCalled();
  });
});
