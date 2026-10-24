import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSolrPanel } from "@/components/fleet-solr-panel";
describe("FleetSolrPanel", () => { it("renders", () => {
    const { container } = render(<FleetSolrPanel collections={10} active={10} documents={200000000} qps={50000} />);
    expect(container.textContent).toContain("Solr");
}); });
