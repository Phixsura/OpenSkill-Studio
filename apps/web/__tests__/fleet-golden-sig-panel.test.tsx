import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGoldenSigPanel } from "@/components/fleet-golden-sig-panel";
describe("FleetGoldenSigPanel", () => { it("renders", () => {
    const { container } = render(<FleetGoldenSigPanel latency={100} traffic={1000} errors={0.5} saturation={60} status="healthy" />);
    expect(container.textContent).toContain("Golden Signals");
    expect(container.textContent).toContain("HEALTHY");
}); });
