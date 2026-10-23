import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBudgetWidget } from "@/components/error-budget-widget";

describe("ErrorBudgetWidget", () => {
  it("renders widget", () => {
    const { container } = render(
      <ErrorBudgetWidget appId="app1" consumedPct={10} remainingPct={90}
        burnRate={0.2} status="healthy" daysRemaining={15} />
    );
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("15d left");
    expect(container.textContent).toContain("0.2x");
  });
});
