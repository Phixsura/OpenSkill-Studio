import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatUsagePanel } from "@/components/feat-usage-panel";
describe("FeatUsagePanel", () => {
  it("renders", () => {
    const { container } = render(
      <FeatUsagePanel totalEvents={5000} unusedCount={3}
        features={[
          { feature: "dark_mode", count: 3000, uniqueUsers: 500 },
          { feature: "export", count: 1000, uniqueUsers: 200 },
        ]} />
    );
    expect(container.textContent).toContain("Feature Usage");
    expect(container.textContent).toContain("5,000 events");
    expect(container.textContent).toContain("3 unused");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("3,000 uses");
    expect(container.textContent).toContain("500 users");
  });
});
