import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContainerSchedView } from "@/components/container-sched-view";

describe("ContainerSchedView", () => {
  it("renders", () => {
    const { container } = render(
      <ContainerSchedView cpuPct={62.5} memPct={55}
        nodes={[
          { name: "node-1", cpuPct: 50, memPct: 50 },
          { name: "node-2", cpuPct: 75, memPct: 60 },
        ]} />
    );
    expect(container.textContent).toContain("Container Scheduler");
    expect(container.textContent).toContain("CPU 62.5%");
    expect(container.textContent).toContain("MEM 55%");
    expect(container.textContent).toContain("node-1");
    expect(container.textContent).toContain("node-2");
  });
});
