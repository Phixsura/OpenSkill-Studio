import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpMaturityPanel } from "@/components/ep-maturity-panel";
describe("EpMaturityPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpMaturityPanel endpoint="/api/users" score={7} total={8} pct={88} level="mature"
        dimensions={{ documentation: 1, testing: 1, monitoring: 1, error_handling: 1,
                      rate_limiting: 1, versioning: 1, auth: 1, caching: 0 }} />
    );
    expect(container.textContent).toContain("Maturity: /api/users");
    expect(container.textContent).toContain("mature");
    expect(container.textContent).toContain("7/8");
    expect(container.textContent).toContain("88%");
    expect(container.textContent).toContain("documentation");
    expect(container.textContent).toContain("caching");
  });
});
