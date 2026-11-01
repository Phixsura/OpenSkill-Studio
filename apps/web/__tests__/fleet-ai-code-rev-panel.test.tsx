import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCodeRevPanel } from "@/components/fleet-ai-code-rev-panel";
describe("FleetAiCodeRevPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCodeRevPanel reviewers={3} active={3} prs={10000} suggestions={30000} accepted={24000} acceptRate={80} />);
    expect(container.textContent).toContain("Code Review");
}); });
