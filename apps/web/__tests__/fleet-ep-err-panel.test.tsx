import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEpErrPanel } from "@/components/fleet-ep-err-panel";
describe("FleetEpErrPanel", () => { it("renders", () => {
    const { container } = render(<FleetEpErrPanel total={50} noisyEndpoints={3} worst="/api/orders" worstRate={12} />);
    expect(container.textContent).toContain("Endpoint Errors");
    expect(container.textContent).toContain("/api/orders");
}); });
