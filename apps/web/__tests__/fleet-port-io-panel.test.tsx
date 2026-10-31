import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPortIoPanel } from "@/components/fleet-port-io-panel";
describe("FleetPortIoPanel", () => { it("renders", () => {
    const { container } = render(<FleetPortIoPanel blueprints={15} entities={1500} actions={50} />);
    expect(container.textContent).toContain("Port.io");
    expect(container.textContent).toContain("1,500 entities");
}); });
