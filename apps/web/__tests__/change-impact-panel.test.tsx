import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangeImpactPanel } from "@/components/change-impact-panel";
describe("ChangeImpactPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ChangeImpactPanel score={80} risk="critical" endpoint="/api/v1/users"
        factors={["breaking_change", "many_consumers", "production"]} />
    );
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("CRITICAL impact");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("breaking change");
    expect(container.textContent).toContain("many consumers");
  });
});
