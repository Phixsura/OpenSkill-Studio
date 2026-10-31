import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxPermissionsPanel } from "@/components/sandbox-permissions-panel";

const mockGrants = [
  { id: "g1", permission: "file:read", status: "granted" as const, isDangerous: false },
  { id: "g2", permission: "exec:subprocess", status: "pending" as const, isDangerous: true },
  { id: "g3", permission: "network:outbound", status: "denied" as const, isDangerous: false },
];

describe("SandboxPermissionsPanel", () => {
  it("renders permissions with status", () => {
    const { container } = render(
      <SandboxPermissionsPanel grants={mockGrants} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("file:read");
    expect(container.textContent).toContain("Granted");
    expect(container.textContent).toContain("1 pending");
  });

  it("shows dangerous badge", () => {
    const { container } = render(
      <SandboxPermissionsPanel grants={mockGrants} extensionName="Test" />
    );
    expect(container.textContent).toContain("Dangerous");
  });

  it("calls onApprove for pending", () => {
    const onApprove = vi.fn();
    const { getByText } = render(
      <SandboxPermissionsPanel grants={mockGrants} extensionName="Test" onApprove={onApprove} />
    );
    fireEvent.click(getByText("Allow"));
    expect(onApprove).toHaveBeenCalledWith("g2");
  });

  it("calls onRevoke for granted", () => {
    const onRevoke = vi.fn();
    const { getByText } = render(
      <SandboxPermissionsPanel grants={mockGrants} extensionName="Test" onRevoke={onRevoke} />
    );
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("g1");
  });
});
