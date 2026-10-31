import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IdempotencyStoreCard from "../src/components/idempotency-store-card";

const entries = [
  { key: "req-abc-123", status_code: 201, is_expired: false, ttl_seconds: 86400 },
  { key: "req-def-456", status_code: 409, is_expired: false, ttl_seconds: 3600 },
  { key: "req-old-789", status_code: 200, is_expired: true, ttl_seconds: 0 },
];

describe("IdempotencyStoreCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <IdempotencyStoreCard entries={entries} totalCount={10} appName="App" />,
    );
    expect(container.textContent).toContain("Idempotency Store");
    expect(container.textContent).toContain("2 active / 10 total");
  });

  it("shows keys", () => {
    const { container } = render(
      <IdempotencyStoreCard entries={entries} totalCount={3} appName="App" />,
    );
    expect(container.textContent).toContain("req-abc-123");
    expect(container.textContent).toContain("req-def-456");
  });

  it("shows status codes and TTL", () => {
    const { container } = render(
      <IdempotencyStoreCard entries={entries} totalCount={3} appName="App" />,
    );
    expect(container.textContent).toContain("201");
    expect(container.textContent).toContain("86400s");
  });

  it("shows empty state", () => {
    const { container } = render(
      <IdempotencyStoreCard entries={[]} totalCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("No cached keys");
  });
});
