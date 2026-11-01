import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelHubPanel } from "@/components/fleet-ai-model-hub-panel";
describe("FleetAiModelHubPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelHubPanel hubs={2} active={2} models={2000} contributors={1000} downloads={500000} />);
    expect(container.textContent).toContain("Model Hub");
}); });
