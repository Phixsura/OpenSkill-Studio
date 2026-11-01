import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyRotationPanel } from "@/components/key-rotation-panel";

const mockKeys = [
  { keyId: "kid_abc", status: "active" as const, createdAt: "2024-01-01", expiresIn: "85 days" },
  { keyId: "kid_old", status: "grace" as const, createdAt: "2023-10-01", expiresIn: "5 days" },
  { keyId: "kid_rev", status: "revoked" as const, createdAt: "2023-06-01" },
];
const mockHistory = [
  { oldKeyId: "kid_old", newKeyId: "kid_abc", reason: "scheduled", timestamp: "2024-01-01" },
];

describe("KeyRotationPanel", () => {
  it("renders keys with status", () => {
    const { container } = render(
      <KeyRotationPanel keys={mockKeys} history={mockHistory} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("kid_abc");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("grace");
  });

  it("calls onRotate", () => {
    const onRotate = vi.fn();
    const { getByText } = render(
      <KeyRotationPanel keys={mockKeys} history={[]} extensionName="Test" onRotate={onRotate} />
    );
    fireEvent.click(getByText("Rotate Now"));
    expect(onRotate).toHaveBeenCalled();
  });

  it("calls onRevoke for active keys", () => {
    const onRevoke = vi.fn();
    const { getAllByText } = render(
      <KeyRotationPanel keys={mockKeys} history={[]} extensionName="Test" onRevoke={onRevoke} />
    );
    fireEvent.click(getAllByText("Revoke")[0]);
    expect(onRevoke).toHaveBeenCalledWith("kid_abc");
  });

  it("shows rotation history", () => {
    const { container } = render(
      <KeyRotationPanel keys={mockKeys} history={mockHistory} extensionName="Test" />
    );
    expect(container.textContent).toContain("kid_old → kid_abc");
    expect(container.textContent).toContain("scheduled");
  });
});
