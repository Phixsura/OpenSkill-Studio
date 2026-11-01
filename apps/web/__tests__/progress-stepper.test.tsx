import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProgressStepper } from "@/components/progress-stepper";

describe("ProgressStepper", () => {
  const steps = [
    { index: 0, label: "Upload", status: "completed", icon: "✓" },
    { index: 1, label: "Process", status: "current", icon: "2" },
    { index: 2, label: "Publish", status: "pending", icon: "3" },
  ];
  it("renders steps", () => {
    const { container } = render(<ProgressStepper steps={steps} progressPct={50} />);
    expect(container.textContent).toContain("Upload");
    expect(container.textContent).toContain("Process");
    expect(container.textContent).toContain("Publish");
    expect(container.textContent).toContain("✓");
  });
});
