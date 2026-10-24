import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqEnrichPanel } from "@/components/req-enrich-panel";
describe("ReqEnrichPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqEnrichPanel applied={2} totalFields={5}
        enrichments={[
          { field: "request_id", source: "generator" },
          { field: "tenant_id", source: "auth" },
        ]} />
    );
    expect(container.textContent).toContain("Request Enrichment");
    expect(container.textContent).toContain("2 enriched");
    expect(container.textContent).toContain("5 total fields");
    expect(container.textContent).toContain("+ request_id");
    expect(container.textContent).toContain("from generator");
  });
});
