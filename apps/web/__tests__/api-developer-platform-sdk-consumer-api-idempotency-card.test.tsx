import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IdempotencyCard from "../src/components/api-developer-platform-sdk-consumer-api-idempotency-card";

describe("IdempotencyCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<IdempotencyCard />);
    expect(container.textContent).toContain("Idempotency Manager");
    expect(container.textContent).toContain("8,420");
    expect(container.textContent).toContain("Active Keys");
  });

  it("shows capacity and TTL", () => {
    const { container } = render(<IdempotencyCard />);
    expect(container.textContent).toContain("8.4%");
    expect(container.textContent).toContain("TTL: 24h");
  });
});
