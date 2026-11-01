import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiIdempotencyKeyStoreCard from "../src/components/api-developer-api-api-idempotency-key-store-card";

describe("APIDeveloperAPIApiIdempotencyKeyStoreCard", () => {
  it("shows idempotency stats", () => {
    const { container } = render(<APIDeveloperAPIApiIdempotencyKeyStoreCard stats={{ active_keys: 1000, total_hits: 250 }} appName="App" />);
    expect(container.textContent).toContain("Idempotency Keys");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("20%");
  });
});
