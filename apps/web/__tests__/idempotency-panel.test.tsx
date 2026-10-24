import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IdempotencyPanel } from "@/components/idempotency-panel";

describe("IdempotencyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IdempotencyPanel activeKeys={3} ttlSeconds={86400}
        keys={[
          { key: "req-abc", hasResponse: true, ageSeconds: 120 },
          { key: "req-def", hasResponse: false, ageSeconds: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Idempotency Keys");
    expect(container.textContent).toContain("3 active");
    expect(container.textContent).toContain("86400s TTL");
    expect(container.textContent).toContain("req-abc");
    expect(container.textContent).toContain("stored");
    expect(container.textContent).toContain("pending");
  });
});
