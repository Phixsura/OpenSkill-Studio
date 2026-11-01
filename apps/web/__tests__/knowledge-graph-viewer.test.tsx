import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KnowledgeGraphViewer } from "@/components/knowledge-graph-viewer";

describe("KnowledgeGraphViewer", () => {
  it("renders graph", () => {
    const { container } = render(
      <KnowledgeGraphViewer nodeCount={3} edgeCount={2} entityTypes={["service", "database"]}
        nodes={[
          { id: "api", type: "service", label: "API" },
          { id: "db", type: "database", label: "Database" },
        ]}
        edges={[{ from: "api", to: "db", type: "uses" }]} />
    );
    expect(container.textContent).toContain("Knowledge Graph");
    expect(container.textContent).toContain("3 nodes");
    expect(container.textContent).toContain("2 edges");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("api →uses→ db");
  });
});
