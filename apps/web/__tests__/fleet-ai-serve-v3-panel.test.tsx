import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiServeV3Panel } from "@/components/fleet-ai-serve-v3-panel";
describe("FleetAiServeV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiServeV3Panel servers={10} active={10} models={500} rps={2000000} p99={20} gpuUtil={90} />);
    expect(container.textContent).toContain("AI Serving v3");
}); });
