import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFalcoPanel } from "@/components/fleet-falco-panel";
describe("FleetFalcoPanel", () => { it("renders", () => {
    const { container } = render(<FleetFalcoPanel nodes={10} active={10} alerts={50} critical={2} clean={false} />);
    expect(container.textContent).toContain("Falco");
    expect(container.textContent).toContain("2 critical");
}); });
