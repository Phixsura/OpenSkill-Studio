import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAcaPanel } from "@/components/fleet-aca-panel";
describe("FleetAcaPanel", () => { it("renders", () => {
    const { container } = render(<FleetAcaPanel apps={10} running={10} replicas={50} revisions={100} />);
    expect(container.textContent).toContain("Container Apps");
}); });
