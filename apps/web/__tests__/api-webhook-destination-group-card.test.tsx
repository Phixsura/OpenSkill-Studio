import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDestinationGroupCard from "../src/components/api-webhook-destination-group-card";

const groups = [
  { group_id: "g1", name: "Production", destination_count: 3, enabled: true },
  { group_id: "g2", name: "Staging", destination_count: 1, enabled: false },
];

describe("APIWebhookDestinationGroupCard", () => {
  it("shows groups", () => {
    const { container } = render(<APIWebhookDestinationGroupCard groups={groups} appName="App" />);
    expect(container.textContent).toContain("Destination Groups");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("3 destinations");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookDestinationGroupCard groups={[]} appName="App" />);
    expect(container.textContent).toContain("No destination groups");
  });
});
