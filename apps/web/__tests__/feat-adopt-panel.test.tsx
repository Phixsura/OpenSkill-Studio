import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatAdoptPanel } from "@/components/feat-adopt-panel";
describe("FeatAdoptPanel", () => {
  it("renders", () => {
    const { container } = render(
      <FeatAdoptPanel totalUsers={1000}
        features={[
          { feature: "dark_mode", uniqueUsers: 500, adoptionPct: 50 },
          { feature: "export", uniqueUsers: 100, adoptionPct: 10 },
        ]} />
    );
    expect(container.textContent).toContain("Feature Adoption");
    expect(container.textContent).toContain("2 features");
    expect(container.textContent).toContain("1,000 users");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("500 users (50%)");
  });
});
