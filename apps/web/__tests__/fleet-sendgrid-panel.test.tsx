import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSendgridPanel } from "@/components/fleet-sendgrid-panel";
describe("FleetSendgridPanel", () => { it("renders", () => {
    const { container } = render(<FleetSendgridPanel accounts={3} active={3} emails={1500000} deliveryRate={98.5} bounceRate={1.5} />);
    expect(container.textContent).toContain("SendGrid");
    expect(container.textContent).toContain("98.5%");
}); });
