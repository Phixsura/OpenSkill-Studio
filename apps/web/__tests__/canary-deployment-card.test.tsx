import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanaryDeploymentCard } from "@/components/canary-deployment-card";

describe("CanaryDeploymentCard", () => {
  it("renders canary", () => {
    const { container } = render(
      <CanaryDeploymentCard stableVersion="1.0" canaryVersion="2.0" canaryPct={10} status="active"
        recommendation="promote" onPromote={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("1.0 (90%)");
    expect(container.textContent).toContain("2.0 (10%)");
    expect(container.textContent).toContain("promote");
  });
  it("calls promote", () => {
    const fn = vi.fn();
    const { container } = render(
      <CanaryDeploymentCard stableVersion="1.0" canaryVersion="2.0" canaryPct={50} status="active"
        recommendation="promote" onPromote={fn} onRollback={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Promote")!);
    expect(fn).toHaveBeenCalled();
  });
});
