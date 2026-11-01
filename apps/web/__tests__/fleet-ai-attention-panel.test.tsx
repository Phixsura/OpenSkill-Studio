import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAttentionPanel } from "@/components/fleet-ai-attention-panel";
describe("FleetAiAttentionPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAttentionPanel analyzers={3} active={3} heads={256} sequences={50000000} sparsity={80} />);
    expect(container.textContent).toContain("AI Attention");
}); });
