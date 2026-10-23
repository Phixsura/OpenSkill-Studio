import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanaryReleaseSlider } from "@/components/canary-release-slider";

describe("CanaryReleaseSlider", () => {
  it("renders", () => {
    const { container } = render(
      <CanaryReleaseSlider baselineVersion="1.0" canaryVersion="1.1" currentPct={10}
        status="active" onAdvance={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Canary Release");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("v1.1");
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("active");
  });
});
