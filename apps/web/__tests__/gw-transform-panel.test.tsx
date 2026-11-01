import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwTransformPanel } from "@/components/gw-transform-panel";
describe("GwTransformPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwTransformPanel totalRules={5}
        rulesApplied={["add_header:X-Request-ID", "rewrite:/api/v1→/internal/v1", "timeout:3000ms"]} />
    );
    expect(container.textContent).toContain("Gateway Transform");
    expect(container.textContent).toContain("3/5 rules applied");
    expect(container.textContent).toContain("add_header:X-Request-ID");
    expect(container.textContent).toContain("rewrite");
    expect(container.textContent).toContain("timeout:3000ms");
  });
});
