import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MetricsExporterCard from "../src/components/api-developer-platform-sdk-consumer-api-metrics-exporter-card";

describe("MetricsExporterCard", () => {
  it("renders title and metrics", () => {
    const { container } = render(<MetricsExporterCard />);
    expect(container.textContent).toContain("Metrics Exporter");
    expect(container.textContent).toContain("http_requests_total");
    expect(container.textContent).toContain("active_connections");
  });

  it("shows types and count", () => {
    const { container } = render(<MetricsExporterCard />);
    expect(container.textContent).toContain("counter");
    expect(container.textContent).toContain("histogram");
    expect(container.textContent).toContain("4 metrics exported");
  });
});
