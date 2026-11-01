import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiUsageChart } from "@/components/api-usage-chart";

describe("ApiUsageChart", () => {
  it("renders usage info", () => {
    const { container } = render(
      <ApiUsageChart totalCalls={5000} quota={10000} usagePct={50}
        topEndpoints={[{ endpoint: "/api/data", count: 3000 }]} />
    );
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("/api/data");
  });
  it("shows red at high usage", () => {
    const { container } = render(
      <ApiUsageChart totalCalls={9500} quota={10000} usagePct={95} topEndpoints={[]} />
    );
    expect(container.textContent).toContain("95%");
    expect(container.querySelector("[class*='bg-red']")).toBeTruthy();
  });
});
