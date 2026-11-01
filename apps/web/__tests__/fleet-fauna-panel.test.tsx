import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFaunaPanel } from "@/components/fleet-fauna-panel";
describe("FleetFaunaPanel", () => { it("renders", () => {
    const { container } = render(<FleetFaunaPanel databases={5} active={5} collections={100} readOps={50000000} />);
    expect(container.textContent).toContain("Fauna");
    expect(container.textContent).toContain("50,000,000");
}); });
