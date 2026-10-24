import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResMonitorPanel } from "@/components/res-monitor-panel";

describe("ResMonitorPanel", () => {
  it("renders resources", () => {
    const { container } = render(
      <ResMonitorPanel avgUsagePct={72} status="critical" criticalCount={1} warningCount={1}
        resources={[
          { name: "CPU", type: "compute", usagePct: 45 },
          { name: "Memory", type: "compute", usagePct: 75 },
          { name: "Disk", type: "storage", usagePct: 95 },
        ]} />
    );
    expect(container.textContent).toContain("Resource Monitor");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("avg 72%");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("45%");
    expect(container.textContent).toContain("Disk");
    expect(container.textContent).toContain("95%");
  });
});
