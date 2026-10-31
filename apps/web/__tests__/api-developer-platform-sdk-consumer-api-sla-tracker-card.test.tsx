import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SlaTrackerCard from "../src/components/api-developer-platform-sdk-consumer-api-sla-tracker-card";

describe("SlaTrackerCard", () => {
  it("renders title and SLAs", () => {
    const { container } = render(<SlaTrackerCard />);
    expect(container.textContent).toContain("SLA Tracker");
    expect(container.textContent).toContain("Uptime %");
    expect(container.textContent).toContain("P99 Latency");
    expect(container.textContent).toContain("Error Rate");
  });

  it("shows compliance and status", () => {
    const { container } = render(<SlaTrackerCard />);
    expect(container.textContent).toContain("compliant");
    expect(container.textContent).toContain("breached");
    expect(container.textContent).toContain("1/3 SLAs met");
  });
});
