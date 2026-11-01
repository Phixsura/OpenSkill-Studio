import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompositeSlaCard } from "@/components/composite-sla-card";

describe("CompositeSlaCard", () => {
  it("renders", () => {
    const { container } = render(
      <CompositeSlaCard compositeSla={99.89} dependencies={3} weakest="api"
        weakestSla={99.9} downtimeMin={43.2} />
    );
    expect(container.textContent).toContain("99.89%");
    expect(container.textContent).toContain("Composite SLA");
    expect(container.textContent).toContain("3 dependencies");
    expect(container.textContent).toContain("43.2min");
    expect(container.textContent).toContain("api");
  });
});
