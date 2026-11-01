import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPiiPanel } from "@/components/fleet-ai-pii-panel";
describe("FleetAiPiiPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPiiPanel services={5} active={5} docs={5000000} piiFound={250000} redacted={250000} />);
    expect(container.textContent).toContain("PII Redaction");
}); });
