import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanaryDeployPanel } from "@/components/canary-deploy-panel";

const deploy = { deployId: "c1", stableVersion: "1.0", canaryVersion: "2.0", rolloutPct: 25, status: "active", errorRate: 1.2, errorThreshold: 5.0 };

describe("CanaryDeployPanel", () => {
  it("renders deploy info", () => {
    const { container } = render(<CanaryDeployPanel deploy={deploy} />);
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("1.2%");
  });
  it("increase rollout", () => {
    const fn = vi.fn();
    const { container } = render(<CanaryDeployPanel deploy={deploy} onIncrease={fn} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Increase"));
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith(50);
  });
});
