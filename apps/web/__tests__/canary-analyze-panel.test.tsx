import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CanaryAnalyzePanel } from "@/components/canary-analyze-panel";
describe("CanaryAnalyzePanel", () => {
  it("renders", () => {
    const { container } = render(
      <CanaryAnalyzePanel verdict="promote" confidencePct={100} errorDelta={0.1}
        latencyDeltaPct={5} successRate={99.4}
        checks={{ err_ok: true, lat_ok: true, success_ok: true }} />
    );
    expect(container.textContent).toContain("Canary Analysis");
    expect(container.textContent).toContain("promote");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("+0.1%");
    expect(container.textContent).toContain("99.4%");
  });
});
