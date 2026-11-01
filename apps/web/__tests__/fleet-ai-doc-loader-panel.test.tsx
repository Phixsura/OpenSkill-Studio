import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDocLoaderPanel } from "@/components/fleet-ai-doc-loader-panel";
describe("FleetAiDocLoaderPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDocLoaderPanel loaders={5} active={5} formats={10} docs={2000000} sizeGb={500} />);
    expect(container.textContent).toContain("Document Loader");
}); });
