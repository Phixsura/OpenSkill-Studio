import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallVelocityChart } from "@/components/install-velocity-chart";

describe("InstallVelocityChart", () => {
  it("renders accelerating", () => {
    const { container } = render(<InstallVelocityChart velocity={25} trend="accelerating" avgDaily={15} recentAvg={20} />);
    expect(container.textContent).toContain("+25%");
    expect(container.textContent).toContain("Accelerating");
    expect(container.textContent).toContain("🚀");
  });
  it("renders decelerating", () => {
    const { container } = render(<InstallVelocityChart velocity={-15} trend="decelerating" avgDaily={20} recentAvg={10} />);
    expect(container.textContent).toContain("-15%");
    expect(container.textContent).toContain("Decelerating");
  });
});
