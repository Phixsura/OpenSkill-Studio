import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiUsageBreakdown } from "@/components/api-usage-breakdown";

describe("ApiUsageBreakdown", () => {
  it("renders breakdown", () => {
    const { container } = render(
      <ApiUsageBreakdown totalRequests={100} uniqueEndpoints={3} breakdown={[
        { endpoint: "GET /users", count: 60, pct: 60, avgMs: 52, errors: 2, errorPct: 3.3 },
        { endpoint: "POST /apps", count: 30, pct: 30, avgMs: 120, errors: 0, errorPct: 0 },
      ]} />
    );
    expect(container.textContent).toContain("API Usage Breakdown");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("52ms");
    expect(container.textContent).toContain("3.3%");
  });
});
