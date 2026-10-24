import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RoutingDashboard } from "@/components/routing-dashboard";

describe("RoutingDashboard", () => {
  it("renders instances", () => {
    const instances = [{ instance_id: "us-east-1", requests: 500, avg_ms: 120 }];
    const { container } = render(<RoutingDashboard instances={instances} totalDecisions={1000} />);
    expect(container.textContent).toContain("us-east-1");
    expect(container.textContent).toContain("1,000 decisions");
  });
  it("shows hot instance warning", () => {
    const { container } = render(
      <RoutingDashboard instances={[]} totalDecisions={100}
        hotInstance={{ instance_id: "overloaded-1", pct: 85 }} />
    );
    expect(container.textContent).toContain("overloaded-1");
    expect(container.textContent).toContain("85%");
  });
});
