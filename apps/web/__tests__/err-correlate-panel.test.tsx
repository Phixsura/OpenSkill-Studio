import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrCorrelatePanel } from "@/components/err-correlate-panel";
describe("ErrCorrelatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ErrCorrelatePanel totalErrors={10} correlatedCount={2}
        cascades={[
          { traceId: "t1", services: ["api", "db"], errorCount: 2, rootService: "api" },
        ]} />
    );
    expect(container.textContent).toContain("Error Correlation");
    expect(container.textContent).toContain("10 errors");
    expect(container.textContent).toContain("2 cascades");
    expect(container.textContent).toContain("t1");
    expect(container.textContent).toContain("root: api");
  });
});
