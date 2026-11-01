import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SloBurnCard } from "@/components/slo-burn-card";

describe("SloBurnCard", () => {
  it("renders", () => {
    const { container } = render(
      <SloBurnCard sloTarget={0.999} alerting={true}
        windows={[
          { window: "1h", burnRate: 14.5, severity: "critical", budgetConsumedPct: 2.01 },
          { window: "6h", burnRate: 1.2, severity: "ok", budgetConsumedPct: 1 },
        ]} />
    );
    expect(container.textContent).toContain("SLO Burn Rate");
    expect(container.textContent).toContain("ALERTING");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("14.5x");
    expect(container.textContent).toContain("1h");
    expect(container.textContent).toContain("2.01% consumed");
  });
});
