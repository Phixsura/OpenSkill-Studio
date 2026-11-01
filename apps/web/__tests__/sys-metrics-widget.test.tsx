import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SysMetricsWidget } from "@/components/sys-metrics-widget";

describe("SysMetricsWidget", () => {
  it("renders metrics", () => {
    const { container } = render(
      <SysMetricsWidget cpuPct={65} memoryPct={72} diskPct={45} networkMbps={150}
        status="warning" alertCount={1} />
    );
    expect(container.textContent).toContain("System Metrics");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("1 alerts");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("Memory");
    expect(container.textContent).toContain("72%");
    expect(container.textContent).toContain("150 Mbps");
  });
});
