import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTraceCtxPanel } from "@/components/fleet-trace-ctx-panel";
describe("FleetTraceCtxPanel", () => { it("renders", () => {
    const { container } = render(<FleetTraceCtxPanel total={30} propagating={28} missing={2} coveragePct={93.3} />);
    expect(container.textContent).toContain("Trace Context");
    expect(container.textContent).toContain("2 missing");
}); });
