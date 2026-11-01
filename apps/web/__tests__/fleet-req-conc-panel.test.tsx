import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReqConcPanel } from "@/components/fleet-req-conc-panel";
describe("FleetReqConcPanel", () => { it("renders", () => {
    const { container } = render(<FleetReqConcPanel totalConc={170} capacity={200} utilPct={85} pressure={true} />);
    expect(container.textContent).toContain("Request Concurrency");
    expect(container.textContent).toContain("High concurrency");
}); });
