import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPostmarkPanel } from "@/components/fleet-postmark-panel";
describe("FleetPostmarkPanel", () => { it("renders", () => {
    const { container } = render(<FleetPostmarkPanel servers={3} active={3} delivered={600000} bounceRate={0.3} />);
    expect(container.textContent).toContain("Postmark");
}); });
