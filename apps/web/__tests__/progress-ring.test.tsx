import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProgressRing } from "@/components/progress-ring";

describe("ProgressRing", () => {
  it("renders", () => {
    const { container } = render(
      <ProgressRing percentage={75} circumference={282.7} offset={70.7} color="blue"
        label="Completion" value={75} maxValue={100} />
    );
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("Completion");
    expect(container.textContent).toContain("75 / 100");
    expect(container.querySelector("svg")).toBeTruthy();
  });
});
