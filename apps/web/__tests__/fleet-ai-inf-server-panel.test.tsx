import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInfServerPanel } from "@/components/fleet-ai-inf-server-panel";
describe("FleetAiInfServerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiInfServerPanel servers={20} healthy={20} rps={500000} ttft={50} tps={1000} />);
    expect(container.textContent).toContain("Inference Server");
}); });
