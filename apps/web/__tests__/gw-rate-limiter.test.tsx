import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwRateLimiter } from "@/components/gw-rate-limiter";

describe("GwRateLimiter", () => {
  it("renders", () => {
    const { container } = render(
      <GwRateLimiter totalBlocked={15} clients={[
        { clientId: "client-1", rpm: 100, current: 85, blocked: 10 },
        { clientId: "client-2", rpm: 50, current: 20, blocked: 5 },
      ]} />
    );
    expect(container.textContent).toContain("Gateway Rate Limits");
    expect(container.textContent).toContain("2 clients");
    expect(container.textContent).toContain("15 blocked");
    expect(container.textContent).toContain("client-1");
    expect(container.textContent).toContain("85/100 rpm");
    expect(container.textContent).toContain("10 blocked");
  });
});
