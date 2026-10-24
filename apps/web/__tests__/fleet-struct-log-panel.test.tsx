import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStructLogPanel } from "@/components/fleet-struct-log-panel";
describe("FleetStructLogPanel", () => { it("renders", () => {
    const { container } = render(<FleetStructLogPanel total={20} structured={18} unstructured={2} mature={false} />);
    expect(container.textContent).toContain("Structured Logging");
    expect(container.textContent).toContain("2 unstructured");
}); });
