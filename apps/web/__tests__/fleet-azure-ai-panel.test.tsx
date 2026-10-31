import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAzureAiPanel } from "@/components/fleet-azure-ai-panel";
describe("FleetAzureAiPanel", () => { it("renders", () => {
    const { container } = render(<FleetAzureAiPanel services={5} active={5} calls={20000000} models={15} />);
    expect(container.textContent).toContain("Azure AI");
}); });
