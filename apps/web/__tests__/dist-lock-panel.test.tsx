import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DistLockPanel } from "@/components/dist-lock-panel";

describe("DistLockPanel", () => {
  it("renders locks", () => {
    const { container } = render(
      <DistLockPanel onRelease={vi.fn()} locks={[
        { resource: "db:migrate", owner: "worker-1", ttlRemaining: 25.3 },
        { resource: "cache:flush", owner: "admin", ttlRemaining: 10 },
      ]} />
    );
    expect(container.textContent).toContain("Distributed Locks");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("db:migrate");
    expect(container.textContent).toContain("worker-1");
    expect(container.textContent).toContain("Force Release");
  });
});
