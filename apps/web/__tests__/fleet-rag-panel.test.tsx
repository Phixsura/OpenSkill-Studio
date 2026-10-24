import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRagPanel } from "@/components/fleet-rag-panel";
describe("FleetRagPanel", () => { it("renders", () => {
    const { container } = render(<FleetRagPanel pipelines={10} active={10} queries={2000000} docsIndexed={50000000} />);
    expect(container.textContent).toContain("RAG");
}); });
