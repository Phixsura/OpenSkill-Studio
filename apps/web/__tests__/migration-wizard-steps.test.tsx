import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MigrationWizardSteps } from "@/components/migration-wizard-steps";

describe("MigrationWizardSteps", () => {
  const steps = [
    { step: 1, type: "code_change", description: "Rename field", automated: true, risk: "low" },
    { step: 2, type: "code_change", description: "Update auth", automated: false, risk: "medium" },
  ];
  it("renders", () => {
    const { container } = render(
      <MigrationWizardSteps fromVersion="2.0" toVersion="3.0" steps={steps} onRunAuto={vi.fn()} />
    );
    expect(container.textContent).toContain("Migration Guide");
    expect(container.textContent).toContain("v2.0 → v3.0");
    expect(container.textContent).toContain("Rename field");
    expect(container.textContent).toContain("Auto");
  });
  it("run auto", () => {
    const fn = vi.fn();
    const { container } = render(
      <MigrationWizardSteps fromVersion="2.0" toVersion="3.0" steps={steps} onRunAuto={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Run Automated Steps")!);
    expect(fn).toHaveBeenCalled();
  });
});
