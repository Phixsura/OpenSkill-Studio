import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOutParserPanel } from "@/components/fleet-ai-out-parser-panel";
describe("FleetAiOutParserPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOutParserPanel parsers={4} active={4} parsed={50000000} formats={8} success={99.5} />);
    expect(container.textContent).toContain("Output Parser");
}); });
