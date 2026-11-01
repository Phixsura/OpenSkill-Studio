import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformSearch } from "@/components/platform-search";

describe("PlatformSearch", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformSearch totalMatches={2} onSearch={vi.fn()}
        byType={{ service: 1, runbook: 1 }}
        results={[
          { name: "API Gateway", type: "service", description: "Routes requests", matchField: "name" },
          { name: "DB Migration", type: "runbook", description: "Migration guide", matchField: "description" },
        ]} />
    );
    expect(container.textContent).toContain("2 results");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("DB Migration");
    expect(container.textContent).toContain("service: 1");
  });
});
