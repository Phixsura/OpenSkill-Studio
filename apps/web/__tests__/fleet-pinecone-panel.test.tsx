import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPineconePanel } from "@/components/fleet-pinecone-panel";
describe("FleetPineconePanel", () => { it("renders", () => {
    const { container } = render(<FleetPineconePanel indexes={5} ready={5} vectors={50000000} qps={5000} />);
    expect(container.textContent).toContain("Pinecone");
    expect(container.textContent).toContain("50,000,000");
}); });
