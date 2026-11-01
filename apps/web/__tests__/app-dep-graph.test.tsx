import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppDepGraph } from "@/components/app-dep-graph";

describe("AppDepGraph", () => {
  it("renders graph", () => {
    const { container } = render(
      <AppDepGraph roots={["gateway"]} leaves={["db"]}
        nodes={[
          { id: "gateway", name: "API Gateway", icon: "🚪" },
          { id: "db", name: "Database", icon: "🗄️" },
        ]}
        edges={[{ from: "gateway", to: "db" }]} />
    );
    expect(container.textContent).toContain("App Dependencies");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("root");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("leaf");
    expect(container.textContent).toContain("→ db");
  });
});
