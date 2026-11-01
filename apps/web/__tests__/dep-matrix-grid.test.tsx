import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepMatrixGrid } from "@/components/dep-matrix-grid";

describe("DepMatrixGrid", () => {
  it("renders matrix", () => {
    const { container } = render(
      <DepMatrixGrid totalDeps={3} densityPct={25}
        services={["api", "db", "cache"]}
        matrix={{
          api: { api: false, db: true, cache: true },
          db: { api: false, db: false, cache: false },
          cache: { api: false, db: false, cache: false },
        }} />
    );
    expect(container.textContent).toContain("Dependency Matrix");
    expect(container.textContent).toContain("3 deps");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
  });
});
