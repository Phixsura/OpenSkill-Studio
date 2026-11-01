import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SloBurnAlert } from "@/components/slo-burn-alert";

describe("SloBurnAlert", () => {
  it("renders", () => {
    const { container } = render(
      <SloBurnAlert burnRate={16.67} budgetConsumedPct={50}
        alertLevel="page" timeToExhaustHours={3} critical={true} />
    );
    expect(container.textContent).toContain("SLO Burn Rate");
    expect(container.textContent).toContain("PAGING");
    expect(container.textContent).toContain("16.67x");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("3h");
  });
});
