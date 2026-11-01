import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseGateChecklist } from "@/components/release-gate-checklist";

describe("ReleaseGateChecklist", () => {
  const gates = [
    { id: "tests", label: "Tests", icon: "🧪", required: true, passed: true, status: "pass" },
    { id: "security", label: "Security", icon: "🔒", required: true, passed: false, status: "fail" },
  ];
  it("renders blocking", () => {
    const { container } = render(
      <ReleaseGateChecklist gates={gates} releaseReady={false} blocking={["security"]} onDeploy={vi.fn()} />
    );
    expect(container.textContent).toContain("Release Gates");
    expect(container.textContent).toContain("❌ 1 blocking");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("Fix blocking");
  });
  it("deploy when ready", () => {
    const fn = vi.fn();
    const readyGates = gates.map(g => ({ ...g, passed: true, status: "pass" }));
    const { container } = render(
      <ReleaseGateChecklist gates={readyGates} releaseReady={true} blocking={[]} onDeploy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Deploy"))!);
    expect(fn).toHaveBeenCalled();
  });
});
