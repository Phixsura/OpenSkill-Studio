import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLogFwdPanel } from "@/components/fleet-log-fwd-panel";
describe("FleetLogFwdPanel", () => { it("renders", () => {
    const { container } = render(<FleetLogFwdPanel agents={5} healthy={5} bufferMb={60} dropped={100} reliable={false} />);
    expect(container.textContent).toContain("Log Forwarding");
    expect(container.textContent).toContain("100 events dropped");
}); });
