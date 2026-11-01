import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClerkPanel } from "@/components/fleet-clerk-panel";
describe("FleetClerkPanel", () => { it("renders", () => {
    const { container } = render(<FleetClerkPanel apps={5} active={5} users={200000} sessions={500000} />);
    expect(container.textContent).toContain("Clerk");
    expect(container.textContent).toContain("200,000");
}); });
