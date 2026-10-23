import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PodHealthGrid } from "@/components/pod-health-grid";

describe("PodHealthGrid", () => {
  it("renders pods", () => {
    const { container } = render(
      <PodHealthGrid health="degraded" running={2} failed={1} totalRestarts={17}
        pods={[
          { name: "api-abc", status: "Running", restarts: 0, cpuPct: 45, memPct: 60 },
          { name: "worker-xyz", status: "CrashLoopBackOff", restarts: 15, cpuPct: 0, memPct: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Pod Health");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("api-abc");
    expect(container.textContent).toContain("CPU 45%");
    expect(container.textContent).toContain("↻15");
    expect(container.textContent).toContain("17 total restarts");
  });
});
