import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManagerPanel } from "@/components/api-key-manager-panel";

const MOCK_KEYS = [
  {
    key_id: "key-1",
    key_prefix: "osk_abc12345...",
    scopes: ["read:skills", "write:projects"],
    status: "active" as const,
    created_at: "2026-10-01T00:00:00Z",
    expires_at: null,
    last_used_at: new Date(Date.now() - 300000).toISOString(),
  },
  {
    key_id: "key-2",
    key_prefix: "osk_def67890...",
    scopes: ["read:skills"],
    status: "revoked" as const,
    created_at: "2026-09-15T00:00:00Z",
    expires_at: "2026-12-15T00:00:00Z",
    last_used_at: null,
  },
  {
    key_id: "key-3",
    key_prefix: "osk_ghi11111...",
    scopes: ["read:skills", "write:projects", "read:email", "admin:org", "execute:sandbox"],
    status: "active" as const,
    created_at: "2026-10-20T00:00:00Z",
    expires_at: null,
    last_used_at: null,
  },
];

const defaultProps = {
  installationId: "inst-1",
  keys: MOCK_KEYS,
  onCreateKey: vi.fn(),
  onRevokeKey: vi.fn(),
  onRotateKey: vi.fn(),
};

describe("ApiKeyManagerPanel", () => {
  it("renders heading and counts", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("3 keys");
    expect(container.textContent).toContain("2 active");
  });

  it("renders key prefixes", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("osk_abc12345...");
    expect(container.textContent).toContain("osk_def67890...");
  });

  it("renders status badges", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("Revoked");
  });

  it("renders scopes", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("read:skills");
    expect(container.textContent).toContain("write:projects");
  });

  it("truncates many scopes with +N more", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("+1 more"); // key-3 has 5 scopes, shows 4
  });

  it("renders last used", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    expect(container.textContent).toMatch(/\d+m ago|Just now/);
    expect(container.textContent).toContain("Never");
  });

  it("calls onCreateKey", () => {
    const onCreateKey = vi.fn();
    const { container } = render(
      <ApiKeyManagerPanel {...defaultProps} onCreateKey={onCreateKey} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("New Key"),
    );
    fireEvent.click(btn!);
    expect(onCreateKey).toHaveBeenCalledOnce();
  });

  it("shows Rotate and Revoke for active keys", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} />);
    const rotateBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Rotate",
    );
    const revokeBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Revoke",
    );
    expect(rotateBtns.length).toBe(2); // 2 active keys
    expect(revokeBtns.length).toBe(2);
  });

  it("calls onRevokeKey", () => {
    const onRevokeKey = vi.fn();
    const { container } = render(
      <ApiKeyManagerPanel {...defaultProps} onRevokeKey={onRevokeKey} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Revoke",
    );
    fireEvent.click(btn!);
    expect(onRevokeKey).toHaveBeenCalledWith("key-1");
  });

  it("calls onRotateKey", () => {
    const onRotateKey = vi.fn();
    const { container } = render(
      <ApiKeyManagerPanel {...defaultProps} onRotateKey={onRotateKey} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Rotate",
    );
    fireEvent.click(btn!);
    expect(onRotateKey).toHaveBeenCalledWith("key-1");
  });

  it("hides actions for revoked keys", () => {
    const revokedOnly = [MOCK_KEYS[1]];
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} keys={revokedOnly} />);
    const actionBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Rotate" || b.textContent === "Revoke",
    );
    expect(actionBtns.length).toBe(0);
  });

  it("shows empty state", () => {
    const { container } = render(<ApiKeyManagerPanel {...defaultProps} keys={[]} />);
    expect(container.textContent).toContain("No API keys yet");
  });
});
