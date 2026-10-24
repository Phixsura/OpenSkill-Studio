import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrPatternPanel } from "@/components/err-pattern-panel";
describe("ErrPatternPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ErrPatternPanel totalErrors={100}
        patterns={[
          { pattern: "timeout", count: 50, services: ["api", "worker"], sample: "Connection timed out" },
          { pattern: "auth_failed", count: 20, services: ["api"], sample: "Invalid token" },
        ]} />
    );
    expect(container.textContent).toContain("Error Patterns");
    expect(container.textContent).toContain("2 patterns");
    expect(container.textContent).toContain("100 errors");
    expect(container.textContent).toContain("timeout");
    expect(container.textContent).toContain("50x");
    expect(container.textContent).toContain("Connection timed out");
  });
});
