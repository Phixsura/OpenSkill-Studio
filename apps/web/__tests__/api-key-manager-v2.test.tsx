import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManagerV2 } from "@/components/api-key-manager-v2";

describe("ApiKeyManagerV2", () => {
  it("renders keys", () => {
    const keys = [{ name: "prod", prefix: "osk_abc123", scopes: ["read"], expires_at: null, usage_count: 500 }];
    const { container } = render(<ApiKeyManagerV2 keys={keys} onCreate={vi.fn()} onRevoke={vi.fn()} />);
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("osk_abc123");
  });
  it("create button", () => {
    const fn = vi.fn();
    const { container } = render(<ApiKeyManagerV2 keys={[]} onCreate={fn} onRevoke={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("New"))!);
    expect(fn).toHaveBeenCalled();
  });
  it("empty state", () => {
    const { container } = render(<ApiKeyManagerV2 keys={[]} onCreate={vi.fn()} onRevoke={vi.fn()} />);
    expect(container.textContent).toContain("No API keys");
  });
});
