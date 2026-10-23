import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTransformEditor } from "@/components/webhook-transform-editor";

describe("WebhookTransformEditor", () => {
  const rules = [
    { action: "rename", path: "user_id", to: "uid" },
    { action: "mask", path: "email" },
  ];
  it("renders", () => {
    const { container } = render(
      <WebhookTransformEditor rules={rules} onAdd={vi.fn()} onRemove={vi.fn()} onTest={vi.fn()} />
    );
    expect(container.textContent).toContain("Webhook Transforms");
    expect(container.textContent).toContain("user_id");
    expect(container.textContent).toContain("uid");
    expect(container.textContent).toContain("🔒 Mask");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(
      <WebhookTransformEditor rules={rules} onAdd={vi.fn()} onRemove={fn} onTest={vi.fn()} />
    );
    const removeBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "×");
    fireEvent.click(removeBtns[0]);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
