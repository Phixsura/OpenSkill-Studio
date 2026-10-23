import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallAnalyticsDashboard } from "@/components/install-analytics-dashboard";

describe("InstallAnalyticsDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <InstallAnalyticsDashboard totalInstalls={500}
        bySource={{ search: 200, referral: 150, direct: 150 }}
        byPlatform={{ web: 350, mobile: 150 }} topSource="search" />
    );
    expect(container.textContent).toContain("Install Analytics");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("🔍 search");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("web");
    expect(container.textContent).toContain("Top source: search");
  });
});
