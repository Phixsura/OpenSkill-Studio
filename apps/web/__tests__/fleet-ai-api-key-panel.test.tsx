import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiKeyPanel } from "@/components/fleet-ai-api-key-panel";
describe("FleetAiApiKeyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiKeyPanel managers={2} active={2} keys={50000} revoked={100} requests={1000000000} />);
    expect(container.textContent).toContain("API Keys");
}); });
