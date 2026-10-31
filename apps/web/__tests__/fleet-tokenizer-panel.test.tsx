import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTokenizerPanel } from "@/components/fleet-tokenizer-panel";
describe("FleetTokenizerPanel", () => { it("renders", () => {
    const { container } = render(<FleetTokenizerPanel services={5} active={5} tokens={5000000000} vocabularies={10} />);
    expect(container.textContent).toContain("Tokenizer");
}); });
