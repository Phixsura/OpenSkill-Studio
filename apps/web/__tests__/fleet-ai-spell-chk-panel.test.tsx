import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSpellChkPanel } from "@/components/fleet-ai-spell-chk-panel";
describe("FleetAiSpellChkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSpellChkPanel checkers={3} active={3} checked={500000000} corrections={20000000} accuracy={99} />);
    expect(container.textContent).toContain("Spell Check");
}); });
