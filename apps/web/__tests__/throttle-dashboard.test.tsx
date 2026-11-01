import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ThrottleDashboard } from "@/components/throttle-dashboard";

describe("ThrottleDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <ThrottleDashboard totalEndpoints={3} healthy={1} throttledCount={2}
        totalBlocked={180} status="throttling"
        throttledEndpoints={[
          { path: "/api/search", blocked: 150, limit: 50, currentRps: 80 },
          { path: "/api/export", blocked: 30, limit: 10, currentRps: 15 },
        ]} />
    );
    expect(container.textContent).toContain("Throttle Dashboard");
    expect(container.textContent).toContain("2 throttled");
    expect(container.textContent).toContain("180 blocked");
    expect(container.textContent).toContain("/api/search");
    expect(container.textContent).toContain("80/50 rps");
  });
});
