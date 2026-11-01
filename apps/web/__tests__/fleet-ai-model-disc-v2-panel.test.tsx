import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelDiscV2Panel } from "@/components/fleet-ai-model-disc-v2-panel";
describe("FleetAiModelDiscV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelDiscV2Panel engines={3} active={3} searches={2000000} models={10000} recommendations={8000000} />);
    expect(container.textContent).toContain("Model Discovery v2");
}); });
