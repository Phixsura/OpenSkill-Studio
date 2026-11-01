import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContainerHealthGrid } from "@/components/container-health-grid";

describe("ContainerHealthGrid", () => {
  it("renders containers", () => {
    const { container } = render(
      <ContainerHealthGrid healthy={1} unhealthy={1} avgCpu={60}
        containers={[
          { name: "api", cpuPct: 30, memoryPct: 50, restartCount: 0, healthy: true, issues: [] },
          { name: "worker", cpuPct: 90, memoryPct: 88, restartCount: 8, healthy: false, issues: ["OOM risk"] },
        ]} />
    );
    expect(container.textContent).toContain("Container Health");
    expect(container.textContent).toContain("1✓");
    expect(container.textContent).toContain("1✗");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("OOM risk");
  });
});
