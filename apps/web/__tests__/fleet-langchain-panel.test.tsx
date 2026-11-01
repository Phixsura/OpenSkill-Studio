import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLangchainPanel } from "@/components/fleet-langchain-panel";
describe("FleetLangchainPanel", () => { it("renders", () => {
    const { container } = render(<FleetLangchainPanel apps={10} deployed={10} chains={50} traces={2000000} />);
    expect(container.textContent).toContain("LangChain");
}); });
