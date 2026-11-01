import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrTrackingDash } from "@/components/err-tracking-dash";

describe("ErrTrackingDash", () => {
  it("renders", () => {
    const { container } = render(
      <ErrTrackingDash totalErrors={50} uniqueTypes={5} topError="TypeError"
        trend="decreasing" pctChange={-25}
        errors={[
          { type: "TypeError", count: 30, services: ["api", "worker"], serviceCount: 2 },
          { type: "ConnectionError", count: 20, services: ["api"], serviceCount: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Error Tracking");
    expect(container.textContent).toContain("50 errors");
    expect(container.textContent).toContain("5 types");
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("30×");
    expect(container.textContent).toContain("25%");
  });
});
