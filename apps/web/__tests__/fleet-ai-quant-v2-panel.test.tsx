import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiQuantV2Panel } from "@/components/fleet-ai-quant-v2-panel";
describe("FleetAiQuantV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiQuantV2Panel quantizers={4} active={4} models={200} bits={4} speedup={5} loss={0.3} />);
    expect(container.textContent).toContain("Quantizer v2");
}); });
