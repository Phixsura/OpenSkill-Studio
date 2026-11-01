import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnHealthPanel } from "@/components/conn-health-panel";
describe("ConnHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ConnHealthPanel healthy={2} total={3}
        connections={[
          { name: "postgres", type: "database", healthy: true, latencyMs: 5 },
          { name: "redis", type: "cache", healthy: true, latencyMs: 2 },
          { name: "ext-api", type: "http", healthy: false, latencyMs: 6000 },
        ]} />
    );
    expect(container.textContent).toContain("Connection Health");
    expect(container.textContent).toContain("2/3 healthy");
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("ext-api");
    expect(container.textContent).toContain("6000ms");
  });
});
