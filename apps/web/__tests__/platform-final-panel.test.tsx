import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformFinalPanel } from "@/components/platform-final-panel";
describe("PlatformFinalPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformFinalPanel overall="fully_operational" score={100}
        modulesOperational={10} totalModules={10} uptimePct={99.99}
        errorRatePct={0.1} rps={10000} p99Ms={100} />
    );
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("10/10 modules");
    expect(container.textContent).toContain("10,000 rps");
    expect(container.textContent).toContain("99.99%");
  });
});
