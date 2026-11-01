import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshAccessLogPanel } from "@/components/mesh-access-log-panel";
describe("MeshAccessLogPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshAccessLogPanel total={100} errors={5}
        entries={[
          { source: "web", destination: "api", method: "GET", path: "/users", status: 200, durationMs: 15 },
          { source: "api", destination: "db", method: "SELECT", path: "orders", status: 500, durationMs: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Access Log");
    expect(container.textContent).toContain("100 entries");
    expect(container.textContent).toContain("5 errors");
    expect(container.textContent).toContain("web→api");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
