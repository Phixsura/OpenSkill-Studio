import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAmplitudePanel } from "@/components/fleet-amplitude-panel";
describe("FleetAmplitudePanel", () => { it("renders", () => {
    const { container } = render(<FleetAmplitudePanel orgs={3} active={3} events={30000000} charts={500} />);
    expect(container.textContent).toContain("Amplitude");
}); });
