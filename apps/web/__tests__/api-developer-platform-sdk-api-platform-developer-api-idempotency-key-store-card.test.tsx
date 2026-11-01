import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-idempotency-key-store-card";

describe("IdempotencyKeyStoreCard", () => {
  it("shows store info", () => {
    const info = { total_keys: 1500, oldest_key_age_hours: 12, hit_rate_pct: 34.5 };
    const recent = [{ key: "k1", method: "POST", path: "/orders", status: 201 }];
    const { container } = render(<Card info={info} recent={recent} appName="App" />);
    expect(container.textContent).toContain("Idempotency Keys");
    expect(container.textContent).toContain("34.5% hit rate");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("12h");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/orders");
  });
  it("shows empty recent", () => {
    const info = { total_keys: 0, oldest_key_age_hours: 0, hit_rate_pct: 0 };
    const { container } = render(<Card info={info} recent={[]} appName="App" />);
    expect(container.textContent).toContain("Idempotency Keys");
    expect(container.textContent).toContain("0");
  });
});
