import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAccessRevPanel } from "@/components/fleet-access-rev-panel";
describe("FleetAccessRevPanel", () => { it("renders", () => {
    const { container } = render(<FleetAccessRevPanel total={50} reviewed={45} pendingReview={5} excessPermissions={3} clean={false} />);
    expect(container.textContent).toContain("Access Review");
    expect(container.textContent).toContain("3 excess");
}); });
