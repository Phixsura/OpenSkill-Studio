import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RetryPolicyEditor } from "@/components/retry-policy-editor";

describe("RetryPolicyEditor", () => {
  it("renders form", () => {
    const { container } = render(
      <RetryPolicyEditor initialMaxRetries={5} initialDelayMs={1000} maxDelayMs={60000} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("Max Retries");
    expect(container.querySelectorAll("input").length).toBe(3);
  });
  it("saves", () => {
    const fn = vi.fn();
    const { container } = render(
      <RetryPolicyEditor initialMaxRetries={5} initialDelayMs={1000} maxDelayMs={60000} onSave={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith({ maxRetries: 5, initialDelayMs: 1000, maxDelayMs: 60000 });
  });
});
