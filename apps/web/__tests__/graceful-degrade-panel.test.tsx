import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GracefulDegradePanel } from "@/components/graceful-degrade-panel";

describe("GracefulDegradePanel", () => {
  it("renders", () => {
    const { container } = render(
      <GracefulDegradePanel level="reduced" active={2} shed={1}
        features={[
          { name: "auth", priority: 10, active: true },
          { name: "analytics", priority: 5, active: true },
          { name: "search", priority: 3, active: false },
        ]} />
    );
    expect(container.textContent).toContain("Degradation Level");
    expect(container.textContent).toContain("reduced");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 shed");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("p10");
    expect(container.textContent).toContain("search");
  });
});
