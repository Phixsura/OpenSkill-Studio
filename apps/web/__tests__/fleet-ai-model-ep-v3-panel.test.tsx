import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelEpV3Panel } from "@/components/fleet-ai-model-ep-v3-panel";
describe("FleetAiModelEpV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelEpV3Panel endpoints={10} active={10} rps={5000000} p50={10} p99={40} />);
    expect(container.textContent).toContain("Model Endpoint v3");
}); });
