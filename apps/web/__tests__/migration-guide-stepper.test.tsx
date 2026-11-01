import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MigrationGuideStepper } from "@/components/migration-guide-stepper";

describe("MigrationGuideStepper", () => {
  it("renders steps", () => {
    const steps = [
      { step: 1, action: "Update permissions", detail: "Remove write scope" },
      { step: 2, action: "Update API", detail: "Switch to v2" },
    ];
    const { container } = render(<MigrationGuideStepper appName="App" steps={steps} effort="high" currentStep={0} />);
    expect(container.textContent).toContain("Migration Guide");
    expect(container.textContent).toContain("Update permissions");
    expect(container.textContent).toContain("Effort: high");
  });
});
