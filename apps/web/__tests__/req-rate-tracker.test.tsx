import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqRateTracker } from "@/components/req-rate-tracker";

describe("ReqRateTracker", () => {
  it("renders", () => {
    const { container } = render(
      <ReqRateTracker totalRps={700} errorPct={1.4} errorRps={10} successRps={685}
        byEndpoint={{ "/api/users": 500, "/api/orders": 200 }} />
    );
    expect(container.textContent).toContain("Request Rates");
    expect(container.textContent).toContain("700 RPS");
    expect(container.textContent).toContain("1.4% errors");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("500 rps");
  });
});
