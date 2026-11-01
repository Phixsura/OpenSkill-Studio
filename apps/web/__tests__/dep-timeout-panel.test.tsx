import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepTimeoutPanel } from "@/components/dep-timeout-panel";
describe("DepTimeoutPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepTimeoutPanel chainTimeoutMs={385} depth={3} valid={true}
        steps={[
          { service: "gateway", timeoutMs: 100, cumulativeMs: 100 },
          { service: "api", timeoutMs: 200, cumulativeMs: 300 },
          { service: "db", timeoutMs: 50, cumulativeMs: 350 },
        ]} />
    );
    expect(container.textContent).toContain("Chain Timeouts");
    expect(container.textContent).toContain("385ms total");
    expect(container.textContent).toContain("depth 3");
    expect(container.textContent).toContain("valid");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("cumulative: 300ms");
  });
});
