import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResendPanel } from "@/components/fleet-resend-panel";
describe("FleetResendPanel", () => { it("renders", () => {
    const { container } = render(<FleetResendPanel domains={5} verified={5} emails={500000} deliveryRate={99} />);
    expect(container.textContent).toContain("Resend");
}); });
