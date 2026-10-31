import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DistLockPanel } from "@/components/dist-lock-panel";

describe("DistLockPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DistLockPanel activeLocks={2} defaultTtl={30}
        locks={[
          { resource: "orders/123", owner: "worker-a", expiresIn: 15 },
          { resource: "users/456", owner: "worker-b", expiresIn: 28 },
        ]} />
    );
    expect(container.textContent).toContain("Distributed Locks");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("30s TTL");
    expect(container.textContent).toContain("orders/123");
    expect(container.textContent).toContain("worker-a");
    expect(container.textContent).toContain("15s left");
  });
});
