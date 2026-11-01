import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcMapExplorer } from "@/components/svc-map-explorer";

describe("SvcMapExplorer", () => {
  it("renders map", () => {
    const { container } = render(
      <SvcMapExplorer serviceCount={3} teams={["platform", "data"]} languages={["python", "typescript"]}
        services={{
          api: { type: "service", team: "platform", language: "python", status: "healthy" },
          db: { type: "database", team: "data", language: "sql", status: "healthy" },
        }}
        connections={[{ from: "api", to: "db" }]} />
    );
    expect(container.textContent).toContain("Service Map");
    expect(container.textContent).toContain("3 services");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("python, typescript");
  });
});
