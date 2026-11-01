import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureHeatmap } from "@/components/feature-heatmap";

describe("FeatureHeatmap", () => {
  it("renders adoption", () => {
    const { container } = render(
      <FeatureHeatmap totalUsers={100} features={["search", "export", "dashboard"]}
        adoption={{
          search: { users: 80, pct: 80 },
          export: { users: 30, pct: 30 },
          dashboard: { users: 95, pct: 95 },
        }} />
    );
    expect(container.textContent).toContain("Feature Adoption");
    expect(container.textContent).toContain("100 users");
    expect(container.textContent).toContain("search");
    expect(container.textContent).toContain("80 users (80%)");
    expect(container.textContent).toContain("export");
    expect(container.textContent).toContain("dashboard");
  });
});
