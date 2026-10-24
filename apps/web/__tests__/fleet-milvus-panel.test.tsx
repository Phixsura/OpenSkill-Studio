import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMilvusPanel } from "@/components/fleet-milvus-panel";
describe("FleetMilvusPanel", () => { it("renders", () => {
    const { container } = render(<FleetMilvusPanel nodes={6} healthy={6} entities={100000000} searchQps={10000} />);
    expect(container.textContent).toContain("Milvus");
    expect(container.textContent).toContain("100,000,000");
}); });
