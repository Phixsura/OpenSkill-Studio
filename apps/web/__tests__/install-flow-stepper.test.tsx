import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallFlowStepper } from "@/components/install-flow-stepper";

describe("InstallFlowStepper", () => {
  it("shows steps", () => {
    const { container } = render(<InstallFlowStepper steps={["review_permissions", "confirm_install"]} currentStep={0} appName="Cool App" />);
    expect(container.textContent).toContain("Review Permissions");
    expect(container.textContent).toContain("Install Cool App");
  });
  it("marks completed", () => {
    const { container } = render(<InstallFlowStepper steps={["review_permissions", "confirm_install"]} currentStep={1} appName="X" />);
    expect(container.textContent).toContain("✓");
  });
});
