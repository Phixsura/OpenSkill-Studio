import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHistoryPanel } from "@/components/fleet-ai-history-panel";
describe("FleetAiHistoryPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHistoryPanel stores={5} active={5} interactions={500000000} storageGb={2000} />);
    expect(container.textContent).toContain("AI History");
}); });
