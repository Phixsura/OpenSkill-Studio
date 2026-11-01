import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WorkloadDist } from "@/components/workload-dist";

describe("WorkloadDist", () => {
  it("renders", () => {
    const { container } = render(
      <WorkloadDist nodes={3} avgLoad={51} spread={7} maxLoad={55}
        minLoad={48} balanced={true} hotspot={null} />
    );
    expect(container.textContent).toContain("Workload Distribution");
    expect(container.textContent).toContain("Balanced");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("51%");
    expect(container.textContent).toContain("55%");
    expect(container.textContent).toContain("7%");
  });
});
