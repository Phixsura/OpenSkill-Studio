import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPrunePanel } from "@/components/fleet-ai-prune-panel";
describe("FleetAiPrunePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPrunePanel pruners={4} active={4} models={60} sparsity={85} accuracyDrop={0.5} />);
    expect(container.textContent).toContain("Model Pruning");
}); });
