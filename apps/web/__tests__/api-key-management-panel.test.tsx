import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManagementPanel } from "@/components/api-key-management-panel";

const mockKeys = [
  { id: "k1", name: "Production", prefix: "osk_abc1", scopes: ["read", "write"], createdAt: "Oct 1", lastUsed: "2m ago", usageCount: 15000, active: true },
  { id: "k2", name: "Old Key", prefix: "osk_xyz9", scopes: ["read"], createdAt: "Sep 1", lastUsed: "30d ago", usageCount: 200, active: false },
];

describe("ApiKeyManagementPanel", () => {
  it("renders keys with details", () => {
    const { container } = render(<ApiKeyManagementPanel keys={mockKeys} />);
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("osk_abc1");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("Revoked");
  });

  it("shows create form on click", () => {
    const { getByText, getByPlaceholderText } = render(<ApiKeyManagementPanel keys={mockKeys} />);
    fireEvent.click(getByText("+ New Key"));
    expect(getByPlaceholderText("Key name (e.g., Production)")).toBeDefined();
  });

  it("calls onRevoke", () => {
    const onRevoke = vi.fn();
    const { getByText } = render(<ApiKeyManagementPanel keys={mockKeys} onRevoke={onRevoke} />);
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("k1");
  });
});
