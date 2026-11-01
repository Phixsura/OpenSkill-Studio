import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalPlatformDashboard } from "@/components/final-platform-dashboard";

describe("FinalPlatformDashboard", () => {
  it("renders dashboard", () => {
    const { container } = render(
      <FinalPlatformDashboard healthDisplay="100/100" status="excellent"
        incidents={0} pendingReviews={3}
        metrics={{
          apps: { value: 500, display: "500" },
          developers: { value: 200, display: "200" },
          mrr: { value: 125000, display: "$125,000" },
          uptime: { value: 99.95, display: "99.95%" },
        }} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("$125,000");
    expect(container.textContent).toContain("99.95%");
  });
});
