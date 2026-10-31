import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IdempotencyKeyViewer } from "@/components/idempotency-key-viewer";

describe("IdempotencyKeyViewer", () => {
  it("renders stats", () => {
    const { container } = render(
      <IdempotencyKeyViewer total={500} active={480} withResponse={450} onCleanup={vi.fn()} />
    );
    expect(container.textContent).toContain("Idempotency Keys");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("480");
    expect(container.textContent).toContain("450");
    expect(container.textContent).toContain("Cleanup Expired");
  });
});
