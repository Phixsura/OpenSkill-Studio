import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVercelAiPanel } from "@/components/fleet-vercel-ai-panel";
describe("FleetVercelAiPanel", () => { it("renders", () => {
    const { container } = render(<FleetVercelAiPanel apps={15} deployed={15} streams={2000000} tokens={500000000} />);
    expect(container.textContent).toContain("Vercel AI");
}); });
