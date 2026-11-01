import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIRequestQuotaPoolCard from "../src/components/api-request-quota-pool-card";

const pools = [
  { pool_id: "p1", name: "Shared Pool", total_capacity: 1000, allocated: 700, available: 300, utilization_pct: 50 },
];

describe("APIRequestQuotaPoolCard", () => {
  it("renders header and pool count", () => {
    const { container } = render(<APIRequestQuotaPoolCard pools={pools} appName="App" />);
    expect(container.textContent).toContain("Quota Pools");
    expect(container.textContent).toContain("1 pools");
  });

  it("shows pool name and allocation", () => {
    const { container } = render(<APIRequestQuotaPoolCard pools={pools} appName="App" />);
    expect(container.textContent).toContain("Shared Pool");
    expect(container.textContent).toContain("700/1000 allocated");
  });

  it("shows empty state", () => {
    const { container } = render(<APIRequestQuotaPoolCard pools={[]} appName="App" />);
    expect(container.textContent).toContain("No quota pools");
  });
});
