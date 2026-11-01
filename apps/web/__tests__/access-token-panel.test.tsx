import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessTokenPanel } from "@/components/access-token-panel";

const mockTokens = [
  { id: "tok_abc", scopes: ["read:data", "write:data"], expiresAt: "2024-12-31",
    revoked: false, useCount: 42, createdAt: "2024-01-01" },
  { id: "tok_xyz", scopes: ["admin:extension"], expiresAt: "2024-06-01",
    revoked: true, useCount: 10, createdAt: "2024-01-01" },
];
const scopes = ["read:data", "write:data", "admin:extension"];

describe("AccessTokenPanel", () => {
  it("renders tokens with scopes", () => {
    const { container } = render(
      <AccessTokenPanel tokens={mockTokens} extensionName="MyExt" availableScopes={scopes} />
    );
    expect(container.textContent).toContain("tok_abc");
    expect(container.textContent).toContain("read:data");
    expect(container.textContent).toContain("1 active");
  });

  it("shows revoked status", () => {
    const { container } = render(
      <AccessTokenPanel tokens={mockTokens} extensionName="Test" availableScopes={scopes} />
    );
    expect(container.textContent).toContain("Revoked");
  });

  it("calls onRevoke", () => {
    const onRevoke = vi.fn();
    const { getByText } = render(
      <AccessTokenPanel tokens={mockTokens} extensionName="Test" availableScopes={scopes} onRevoke={onRevoke} />
    );
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("tok_abc");
  });

  it("opens create form with scope selection", () => {
    const onIssue = vi.fn();
    const { getByText } = render(
      <AccessTokenPanel tokens={[]} extensionName="Test" availableScopes={scopes} onIssue={onIssue} />
    );
    fireEvent.click(getByText("+ New Token"));
    fireEvent.click(getByText("read:data"));
    fireEvent.click(getByText("Issue Token"));
    expect(onIssue).toHaveBeenCalledWith(["read:data"]);
  });
});
