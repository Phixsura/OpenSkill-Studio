import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlowQueryPanel } from "@/components/slow-query-panel";
describe("SlowQueryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SlowQueryPanel thresholdMs={50} total={2}
        queries={[
          { query: "SELECT * FROM orders WHERE id = ?", durationMs: 200, table: "orders" },
          { query: "UPDATE users SET name = ?", durationMs: 150, table: "users" },
        ]} />
    );
    expect(container.textContent).toContain("Slow Queries");
    expect(container.textContent).toContain("2 slow");
    expect(container.textContent).toContain(">50ms");
    expect(container.textContent).toContain("orders");
    expect(container.textContent).toContain("200ms");
  });
});
