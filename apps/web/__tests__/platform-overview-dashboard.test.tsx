import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOverviewDashboard } from "@/components/platform-overview-dashboard";

describe("PlatformOverviewDashboard", () => {
  it("renders overview", () => {
    const { container } = render(
      <PlatformOverviewDashboard healthDisplay="100/100" status="excellent"
        milestone="🏆 2,100 COMMITS"
        metrics={{
          apps: { value: 250, display: "250" },
          developers: { value: 1500, display: "1,500" },
          mrr: { value: 45000, display: "$45,000" },
        }} />
    );
    expect(container.textContent).toContain("Platform Overview");
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("$45,000");
    expect(container.textContent).toContain("2,100 COMMITS");
  });
});
