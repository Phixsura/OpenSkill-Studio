import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIUsageBreakdownCard from "../src/components/api-usage-breakdown-card";

const topEndpoints = [{ name: "/api/users", count: 500 }, { name: "/api/apps", count: 200 }];
const methodBreakdown = { GET: 600, POST: 100 };

describe("APIUsageBreakdownCard", () => {
  it("renders header and methods", () => {
    const { container } = render(<APIUsageBreakdownCard topEndpoints={topEndpoints} methodBreakdown={methodBreakdown} appName="App" />);
    expect(container.textContent).toContain("Usage Breakdown");
    expect(container.textContent).toContain("GET: 600");
  });

  it("shows top endpoints", () => {
    const { container } = render(<APIUsageBreakdownCard topEndpoints={topEndpoints} methodBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("500");
  });

  it("shows empty state", () => {
    const { container } = render(<APIUsageBreakdownCard topEndpoints={[]} methodBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
