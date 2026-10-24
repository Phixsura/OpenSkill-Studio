import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IdempotencyKeyInfo } from "@/components/idempotency-key-info";

describe("IdempotencyKeyInfo", () => {
  it("renders", () => {
    const { container } = render(
      <IdempotencyKeyInfo apiKey="idem_abc123" expiresAt="2026-10-24T12:00:00"
        onGenerate={vi.fn()} onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("Idempotency Key");
    expect(container.textContent).toContain("idem_abc123");
    expect(container.textContent).toContain("Expires:");
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(
      <IdempotencyKeyInfo apiKey="idem_xyz" expiresAt="2026-10-24T00:00:00"
        onGenerate={vi.fn()} onCopy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalledWith("idem_xyz");
  });
});
