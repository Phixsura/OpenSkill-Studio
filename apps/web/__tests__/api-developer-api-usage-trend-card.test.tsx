import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIUsageTrendCard from "../src/components/api-developer-api-usage-trend-card";

const data = [
  { period: "2024-01", requests: 10000, error_rate: 1.0 },
  { period: "2024-02", requests: 12000, error_rate: 0.8 },
];

describe("APIDeveloperAPIUsageTrendCard", () => {
  it("shows trend", () => {
    const { container } = render(<APIDeveloperAPIUsageTrendCard data={data} growthRate={20} appName="App" />);
    expect(container.textContent).toContain("Usage Trend");
    expect(container.textContent).toContain("+20%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIUsageTrendCard data={[]} growthRate={0} appName="App" />);
    expect(container.textContent).toContain("No trend data");
  });
});
