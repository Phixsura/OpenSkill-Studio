import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StepIndicator } from "@/components/step-indicator";

describe("StepIndicator", () => {
  const steps = [
    { index: 0, label: "Start", status: "completed" },
    { index: 1, label: "Config", status: "current" },
    { index: 2, label: "Deploy", status: "upcoming" },
  ];
  it("renders", () => {
    const { container } = render(<StepIndicator steps={steps} progressPct={50} />);
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Start");
    expect(container.textContent).toContain("Config");
    expect(container.textContent).toContain("Deploy");
  });
});
