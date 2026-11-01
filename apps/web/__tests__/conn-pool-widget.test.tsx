import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnPoolWidget } from "@/components/conn-pool-widget";

describe("ConnPoolWidget", () => {
  it("renders", () => {
    const { container } = render(
      <ConnPoolWidget pools={[
        { name: "postgres", active: 15, idle: 5, maxSize: 20, utilizationPct: 75, waits: 3 },
        { name: "redis", active: 2, idle: 8, maxSize: 10, utilizationPct: 20, waits: 0 },
      ]} />
    );
    expect(container.textContent).toContain("Connection Pools");
    expect(container.textContent).toContain("2 pools");
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("15/20 active");
    expect(container.textContent).toContain("3 waits");
    expect(container.textContent).toContain("redis");
  });
});
