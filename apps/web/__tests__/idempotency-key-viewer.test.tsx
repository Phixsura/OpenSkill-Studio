import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IdempotencyKeyViewer } from "@/components/idempotency-key-viewer";

describe("IdempotencyKeyViewer", () => {
  it("renders keys", () => {
    const { container } = render(
      <IdempotencyKeyViewer trackedKeys={5} ttlSec={3600}
        recentKeys={[
          { key: "pay_abc123def", age: "2m" },
          { key: "pay_xyz789ghi", age: "5m" },
        ]} />
    );
    expect(container.textContent).toContain("Idempotency Keys");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("3600s");
    expect(container.textContent).toContain("pay_abc123def");
    expect(container.textContent).toContain("2m ago");
  });
});
