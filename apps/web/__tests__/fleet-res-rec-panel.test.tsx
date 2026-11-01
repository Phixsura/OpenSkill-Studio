import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResRecPanel } from "@/components/fleet-res-rec-panel";
describe("FleetResRecPanel", () => { it("renders", () => {
    const { container } = render(<FleetResRecPanel total={10} overProv={3} underProv={1} rightSized={6} savingsPossible={true} />);
    expect(container.textContent).toContain("Resource Recommendations");
    expect(container.textContent).toContain("Cost savings");
}); });
