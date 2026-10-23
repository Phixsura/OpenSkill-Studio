import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MetricsExportPanel } from "@/components/metrics-export-panel";

describe("MetricsExportPanel", () => {
  const metrics = [
    { name: "app.requests", value: 150000, type: "counter", help: "Total" },
    { name: "app.latency", value: 0.25, type: "gauge", help: "P99" },
  ];
  it("renders", () => {
    const { container } = render(
      <MetricsExportPanel metrics={metrics} prometheusContent="# HELP..."
        onCopy={vi.fn()} onDownload={vi.fn()} />
    );
    expect(container.textContent).toContain("Metrics Export");
    expect(container.textContent).toContain("150,000");
    expect(container.textContent).toContain("0.250");
    expect(container.textContent).toContain("Prometheus Format");
  });
});
