import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSoc2Panel } from "@/components/fleet-soc2-panel";
describe("FleetSoc2Panel", () => { it("renders", () => {
    const { container } = render(<FleetSoc2Panel total={50} implemented={48} tested={45} ready={false} />);
    expect(container.textContent).toContain("SOC2");
    expect(container.textContent).toContain("Not audit ready");
}); });
