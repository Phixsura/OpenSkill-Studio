import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDocParsePanel } from "@/components/fleet-ai-doc-parse-panel";
describe("FleetAiDocParsePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDocParsePanel parsers={5} active={5} docs={5000000} fields={200000000} accuracy={99} />);
    expect(container.textContent).toContain("Document Parsing");
}); });
