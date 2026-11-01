import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepMatrixPanel } from "@/components/dep-matrix-panel";
describe("DepMatrixPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepMatrixPanel services={["api", "db"]} healthPct={100}
        healthyPairs={1} totalPairs={1}
        matrix={{ api: { db: "healthy" }, db: {} }} />
    );
    expect(container.textContent).toContain("Dependency Matrix");
    expect(container.textContent).toContain("1/1 healthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
  });
});
