import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpensearchPanel } from "@/components/fleet-opensearch-panel";
describe("FleetOpensearchPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpensearchPanel clusters={3} green={3} documents={500000000} shards={600} />);
    expect(container.textContent).toContain("OpenSearch");
}); });
