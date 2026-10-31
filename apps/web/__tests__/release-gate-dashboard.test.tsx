import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseGateDashboard } from "@/components/release-gate-dashboard";

const mockChecks = [
  { name: "Tests", status: "passed" as const, required: true, message: "All 42 tests passed" },
  { name: "Security Scan", status: "passed" as const, required: true, message: "" },
  { name: "Compliance", status: "failed" as const, required: true, message: "Missing license file" },
  { name: "Documentation", status: "skipped" as const, required: false, message: "" },
];

describe("ReleaseGateDashboard", () => {
  it("renders checks with status", () => {
    const { container } = render(
      <ReleaseGateDashboard extensionName="Slack Bot" version="2.0.0" checks={mockChecks} canRelease={false} />
    );
    expect(container.textContent).toContain("Release Gate");
    expect(container.textContent).toContain("Slack Bot v2.0.0");
    expect(container.textContent).toContain("Tests");
    expect(container.textContent).toContain("Blocked");
    expect(container.textContent).toContain("2 passed");
    expect(container.textContent).toContain("1 failed");
  });

  it("shows rerun for failed checks", () => {
    const onRerun = vi.fn();
    const { getByText } = render(
      <ReleaseGateDashboard extensionName="Test" version="1.0" checks={mockChecks} canRelease={false} onRerun={onRerun} />
    );
    fireEvent.click(getByText("🔄 Rerun"));
    expect(onRerun).toHaveBeenCalledWith("Compliance");
  });

  it("enables release when ready", () => {
    const onRelease = vi.fn();
    const allPassed = mockChecks.map((c) => ({ ...c, status: "passed" as const }));
    const { getByText } = render(
      <ReleaseGateDashboard extensionName="Test" version="2.0" checks={allPassed} canRelease={true} onRelease={onRelease} />
    );
    expect(getByText("🚀 Release v2.0")).toBeDefined();
    fireEvent.click(getByText("🚀 Release v2.0"));
    expect(onRelease).toHaveBeenCalled();
  });
});
