import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSecretManager } from "@/components/webhook-secret-manager";

const secs = [
  { secretId: "whsec-2", createdAt: Date.now(), expiresAt: 0, active: true, masked: "whsec_****abcd" },
  { secretId: "whsec-1", createdAt: Date.now() - 10000, expiresAt: Date.now() + 300000, active: true, masked: "whsec_****1234" },
];

describe("WebhookSecretManager", () => {
  it("renders secrets", () => {
    const { container } = render(<WebhookSecretManager secrets={secs} />);
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("Grace period");
  });
  it("rotate button", () => {
    const fn = vi.fn();
    const { container } = render(<WebhookSecretManager secrets={secs} onRotate={fn} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Rotate"));
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalled();
  });
});
