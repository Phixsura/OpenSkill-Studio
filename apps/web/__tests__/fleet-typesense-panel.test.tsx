import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTypesensePanel } from "@/components/fleet-typesense-panel";
describe("FleetTypesensePanel", () => { it("renders", () => {
    const { container } = render(<FleetTypesensePanel nodes={3} healthy={3} collections={50} documents={50000000} />);
    expect(container.textContent).toContain("Typesense");
    expect(container.textContent).toContain("50,000,000");
}); });
