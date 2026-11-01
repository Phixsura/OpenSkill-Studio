import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiServerlessPanel } from "@/components/fleet-ai-serverless-panel";
describe("FleetAiServerlessPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiServerlessPanel functions={20} active={20} invocations={50000000} coldStart={150} cost={0.3} />);
    expect(container.textContent).toContain("Serverless");
}); });
