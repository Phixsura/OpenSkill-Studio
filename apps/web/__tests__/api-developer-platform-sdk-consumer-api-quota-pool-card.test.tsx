import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import QuotaPoolCard from "../src/components/api-developer-platform-sdk-consumer-api-quota-pool-card";

describe("QuotaPoolCard", () => {
  it("renders title and pools", () => {
    const { container } = render(<QuotaPoolCard />);
    expect(container.textContent).toContain("Quota Pools");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("Storage MB");
  });

  it("shows utilization and capacity", () => {
    const { container } = render(<QuotaPoolCard />);
    expect(container.textContent).toContain("75% used");
    expect(container.textContent).toContain("2 pools active");
  });
});
