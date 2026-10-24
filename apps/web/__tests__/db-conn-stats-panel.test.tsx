import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DbConnStatsPanel } from "@/components/db-conn-stats-panel";

describe("DbConnStatsPanel", () => {
  it("renders stats", () => {
    const { container } = render(
      <DbConnStatsPanel active={20} idle={10} max={40} waiting={3}
        utilizationPct={50} health="healthy"
        recommendations={["Consider scaling"]} />
    );
    expect(container.textContent).toContain("DB Connections");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("Consider scaling");
  });
});
