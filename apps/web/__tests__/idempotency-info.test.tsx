import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IdempotencyInfo } from "@/components/idempotency-info";

describe("IdempotencyInfo", () => {
  it("new request", () => {
    const { container } = render(
      <IdempotencyInfo key_="idem_abc" isDuplicate={false} hasConflict={false} cachedResponse={null} originalAt={null} />
    );
    expect(container.textContent).toContain("New Request");
  });
  it("duplicate", () => {
    const { container } = render(
      <IdempotencyInfo key_="idem_abc" isDuplicate={true} hasConflict={false}
        cachedResponse={{ id: "created" }} originalAt="2026-01-01" />
    );
    expect(container.textContent).toContain("Duplicate");
    expect(container.textContent).toContain("created");
  });
});
