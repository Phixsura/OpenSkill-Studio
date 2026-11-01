import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcBlueprintViewer } from "@/components/svc-blueprint-viewer";

describe("SvcBlueprintViewer", () => {
  it("renders", () => {
    const { container } = render(
      <SvcBlueprintViewer name="api-stack" estimatedMonthlyCost={900} valid={true} issues={[]}
        components={[
          { name: "api", type: "service", estimatedCost: 500 },
          { name: "db", type: "database", estimatedCost: 300 },
          { name: "cache", type: "cache", estimatedCost: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Blueprint: api-stack");
    expect(container.textContent).toContain("$900/mo");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("cache");
  });
});
