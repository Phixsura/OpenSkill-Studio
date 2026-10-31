import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CapacityPlannerCard from "../src/components/api-developer-platform-sdk-consumer-api-capacity-planner-card";

describe("CapacityPlannerCard", () => {
  it("renders title and resources", () => {
    const { container } = render(<CapacityPlannerCard />);
    expect(container.textContent).toContain("Capacity Planner");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("Storage");
  });

  it("shows status counts", () => {
    const { container } = render(<CapacityPlannerCard />);
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("1 warning");
  });
});
