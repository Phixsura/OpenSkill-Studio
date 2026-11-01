import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelRbV2Panel } from "@/components/fleet-ai-model-rb-v2-panel";
describe("FleetAiModelRbV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelRbV2Panel managers={4} active={4} rollbacks={20} avgTime={3} successRate={100} />);
    expect(container.textContent).toContain("Model Rollback v2");
}); });
