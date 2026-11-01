import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyScopePanel } from "@/components/api-key-scope-panel";

const mockKeys = [
  { keyId: "k1", name: "prod-key", scopes: ["read:data", "write:data"], usageCount: 150,
    maxUsage: 0, revoked: false, hasIpRestriction: true, hasExpiry: false },
  { keyId: "k2", name: "temp-key", scopes: ["read:data"], usageCount: 10,
    maxUsage: 100, revoked: false, hasIpRestriction: false, hasExpiry: true },
  { keyId: "k3", name: "old-key", scopes: ["admin:sandbox"], usageCount: 500,
    maxUsage: 0, revoked: true, hasIpRestriction: false, hasExpiry: false },
];
const scopes = ["read:data", "write:data", "execute:function", "admin:sandbox"];

describe("ApiKeyScopePanel", () => {
  it("renders keys with scopes", () => {
    const { container } = render(<ApiKeyScopePanel keys={mockKeys} availableScopes={scopes} />);
    expect(container.textContent).toContain("prod-key");
    expect(container.textContent).toContain("read:data");
    expect(container.textContent).toContain("2 active");
  });

  it("shows revoked status", () => {
    const { container } = render(<ApiKeyScopePanel keys={mockKeys} availableScopes={scopes} />);
    expect(container.textContent).toContain("revoked");
  });

  it("calls onRevoke", () => {
    const onRevoke = vi.fn();
    const { getAllByText } = render(<ApiKeyScopePanel keys={mockKeys} availableScopes={scopes} onRevoke={onRevoke} />);
    fireEvent.click(getAllByText("Revoke")[0]);
    expect(onRevoke).toHaveBeenCalledWith("k1");
  });

  it("opens create form", () => {
    const { getByText, getByPlaceholderText } = render(
      <ApiKeyScopePanel keys={[]} availableScopes={scopes} />
    );
    fireEvent.click(getByText("+ New Key"));
    expect(getByPlaceholderText("Key name")).toBeDefined();
  });
});
