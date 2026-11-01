import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageMeteringCard from "../src/components/usage-metering-card";

const metrics = [
  { metric: "api_calls", total: 15000, periods: 30 },
  { metric: "storage_mb", total: 512, periods: 15 },
];

describe("UsageMeteringCard", () => {
  it("renders header and count", () => {
    const { container } = render(<UsageMeteringCard metrics={metrics} appName="App" />);
    expect(container.textContent).toContain("Usage Metering");
    expect(container.textContent).toContain("2 metrics");
  });

  it("shows metric names and totals", () => {
    const { container } = render(<UsageMeteringCard metrics={metrics} appName="App" />);
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("storage_mb");
  });

  it("shows period counts", () => {
    const { container } = render(<UsageMeteringCard metrics={metrics} appName="App" />);
    expect(container.textContent).toContain("30 periods");
  });

  it("shows empty state", () => {
    const { container } = render(<UsageMeteringCard metrics={[]} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
