import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPayloadPanel } from "@/components/fleet-payload-panel";
describe("FleetPayloadPanel", () => { it("renders", () => {
    const { container } = render(<FleetPayloadPanel instances={3} running={3} collections={50} documents={500000} />);
    expect(container.textContent).toContain("Payload");
    expect(container.textContent).toContain("500,000 docs");
}); });
