import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiKeyAuditTrailCard from "../src/components/api-developer-platform-sdk-api-key-audit-trail-card";

const entries = [
  { entry_id: "e1", key_id: "sk-prod-1", action: "created", actor: "admin@acme.com" },
  { entry_id: "e2", key_id: "sk-prod-1", action: "rotated", actor: "admin@acme.com" },
];

describe("Card", () => {
  it("shows audit trail", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiKeyAuditTrailCard entries={entries} actionCounts={{ created: 1, rotated: 1 }} appName="App" />);
    expect(container.textContent).toContain("Key Audit Trail");
    expect(container.textContent).toContain("sk-prod-1");
    expect(container.textContent).toContain("created by admin@acme.com");
    expect(container.textContent).toContain("rotated: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiKeyAuditTrailCard entries={[]} actionCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No audit entries");
  });
});
