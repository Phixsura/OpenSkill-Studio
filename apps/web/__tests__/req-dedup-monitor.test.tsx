import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqDedupMonitor } from "@/components/req-dedup-monitor";

describe("ReqDedupMonitor", () => {
  it("renders with dups", () => {
    const { container } = render(
      <ReqDedupMonitor cachedKeys={5} ttlSeconds={60}
        recentDups={[
          { key: "abc12345", method: "POST", path: "/api/orders" },
        ]} />
    );
    expect(container.textContent).toContain("Request Dedup");
    expect(container.textContent).toContain("5 cached");
    expect(container.textContent).toContain("60s TTL");
    expect(container.textContent).toContain("POST /api/orders");
  });
  it("renders empty", () => {
    const { container } = render(
      <ReqDedupMonitor cachedKeys={0} ttlSeconds={30} recentDups={[]} />
    );
    expect(container.textContent).toContain("No recent duplicates");
  });
});
