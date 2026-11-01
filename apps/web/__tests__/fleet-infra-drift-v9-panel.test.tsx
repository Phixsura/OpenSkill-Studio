import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInfraDriftV9Panel } from "@/components/fleet-infra-drift-v9-panel";
describe("FleetInfraDriftV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetInfraDriftV9Panel stacks={30} drifted={0} />);
    expect(container.textContent).toContain("Infra Drift v9");
}); });
