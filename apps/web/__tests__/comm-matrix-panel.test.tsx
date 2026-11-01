import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommMatrixPanel } from "@/components/comm-matrix-panel";
describe("CommMatrixPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CommMatrixPanel services={["api", "db"]} totalComms={5000}
        rows={[
          { service: "api", api: 0, db: 5000 },
          { service: "db", api: 0, db: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Communication Matrix");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("5,000 calls");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
  });
});
