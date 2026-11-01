import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIngressCtrlV9Panel } from "@/components/fleet-ingress-ctrl-v9-panel";
describe("FleetIngressCtrlV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIngressCtrlV9Panel rules={30} rps={50000} />);
    expect(container.textContent).toContain("Ingress Controller v9");
}); });
