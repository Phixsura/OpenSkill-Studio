import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAnsiblePanel } from "@/components/fleet-ansible-panel";
describe("FleetAnsiblePanel", () => { it("renders", () => {
    const { container } = render(<FleetAnsiblePanel total={50} ok={45} changed={3} failed={2} />);
    expect(container.textContent).toContain("Ansible");
}); });
