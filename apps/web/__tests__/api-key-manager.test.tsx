import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManager } from "@/components/api-key-manager";

const keys = [
  { keyId: "k1", prefix: "osk_abc12345", name: "Production", scopes: ["read", "write"], active: true, expiresAt: Date.now() / 1000 + 86400 * 30 },
];

describe("ApiKeyManager", () => {
  it("renders keys", () => {
    const { container } = render(<ApiKeyManager keys={keys} />);
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("osk_abc12345");
    expect(container.textContent).toContain("read");
  });
  it("rotate key", () => {
    const fn = vi.fn();
    const { container } = render(<ApiKeyManager keys={keys} onRotate={fn} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Rotate");
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("k1");
  });
});
