import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDocGenPanel } from "@/components/fleet-ai-doc-gen-panel";
describe("FleetAiDocGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDocGenPanel generators={3} active={3} pages={50000} repos={1000} freshness={97} />);
    expect(container.textContent).toContain("Doc Generation");
}); });
