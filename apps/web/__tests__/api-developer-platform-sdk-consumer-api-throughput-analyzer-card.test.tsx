import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ThroughputAnalyzerCard from "../src/components/api-developer-platform-sdk-consumer-api-throughput-analyzer-card";

describe("ThroughputAnalyzerCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<ThroughputAnalyzerCard />);
    expect(container.textContent).toContain("Throughput Analyzer");
    expect(container.textContent).toContain("ep-users");
    expect(container.textContent).toContain("ep-search");
  });

  it("shows capacity status and metrics", () => {
    const { container } = render(<ThroughputAnalyzerCard />);
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("stressed");
    expect(container.textContent).toContain("Peak RPS");
    expect(container.textContent).toContain("480");
  });
});
