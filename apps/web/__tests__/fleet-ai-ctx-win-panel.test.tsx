import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCtxWinPanel } from "@/components/fleet-ai-ctx-win-panel";
describe("FleetAiCtxWinPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCtxWinPanel managers={4} active={4} maxTokens={2000000} usage={70} overflows={0} />);
    expect(container.textContent).toContain("Context Window");
}); });
