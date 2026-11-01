import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StepProgressBar } from "@/components/step-progress-bar";

describe("StepProgressBar", () => {
  it("renders progress", () => {
    const { container } = render(
      <StepProgressBar title="Setup" pct={50} completedCount={2} total={4}
        steps={[
          { index: 0, label: "Create", completed: true },
          { index: 1, label: "Configure", completed: true },
          { index: 2, label: "Deploy", completed: false },
          { index: 3, label: "Verify", completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Setup");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("2/4 complete");
    expect(container.textContent).toContain("Create");
    expect(container.textContent).toContain("Deploy");
  });
});
