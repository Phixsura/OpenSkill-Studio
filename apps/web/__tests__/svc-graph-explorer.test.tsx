import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcGraphExplorer } from "@/components/svc-graph-explorer";

describe("SvcGraphExplorer", () => {
  it("renders", () => {
    const { container } = render(
      <SvcGraphExplorer nodeCount={4} edgeCount={3} healthy={4} teams={["frontend", "platform", "data"]}
        nodes={[
          { id: "web", type: "service", team: "frontend", healthy: true },
          { id: "api", type: "service", team: "platform", healthy: true },
          { id: "db", type: "database", team: "data", healthy: true },
        ]} />
    );
    expect(container.textContent).toContain("Service Graph");
    expect(container.textContent).toContain("4 services");
    expect(container.textContent).toContain("3 deps");
    expect(container.textContent).toContain("web");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("frontend, platform, data");
  });
});
