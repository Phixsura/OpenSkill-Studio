import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-deduplication-card";

describe("RequestDeduplicationCard", () => {
  it("shows entries", () => {
    const entries = [{ key: "idem-abc-123", status: 200, createdAt: "12:00", expiresAt: "13:00" }];
    const { container } = render(<Card entries={entries} ttlHours={24} appName="App" />);
    expect(container.textContent).toContain("Request Deduplication");
    expect(container.textContent).toContain("idem-abc-123");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("TTL: 24h");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} ttlHours={1} appName="App" />);
    expect(container.textContent).toContain("No cached idempotency keys");
  });
});
