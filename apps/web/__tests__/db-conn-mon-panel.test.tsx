import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DbConnMonPanel } from "@/components/db-conn-mon-panel";
describe("DbConnMonPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DbConnMonPanel utilPct={65} healthy={false} saturated={["analytics"]}
        pools={[
          { name: "primary", active: 15, maxSize: 20 },
          { name: "analytics", active: 19, maxSize: 20 },
        ]} />
    );
    expect(container.textContent).toContain("DB Connections");
    expect(container.textContent).toContain("65% util");
    expect(container.textContent).toContain("1 saturated");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("15/20");
    expect(container.textContent).toContain("19/20");
  });
});
