import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrandSummaryPage } from "@/components/grand-summary-page";

describe("GrandSummaryPage", () => {
  it("renders grand summary", () => {
    const { container } = render(
      <GrandSummaryPage milestone="2,200 COMMITS" achievement="🏆 TWO THOUSAND TWO HUNDRED!"
        status="FULLY OPERATIONAL"
        stats={{ commits: 2200, lines: 193000, files: 6314, services: 1100, components: 1100, tests: 2200 }}
        modules={["Extension SDK", "Sandboxed Apps", "Marketplace", "Automation API"]} />
    );
    expect(container.textContent).toContain("2,200 COMMITS");
    expect(container.textContent).toContain("193,000");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("Platform Modules");
  });
});
