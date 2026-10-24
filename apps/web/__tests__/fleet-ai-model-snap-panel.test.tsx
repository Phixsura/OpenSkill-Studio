import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelSnapPanel } from "@/components/fleet-ai-model-snap-panel";
describe("FleetAiModelSnapPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelSnapPanel managers={3} active={3} snapshots={50000} storageTb={2000} restorations={100} />);
    expect(container.textContent).toContain("Model Snapshot");
}); });
