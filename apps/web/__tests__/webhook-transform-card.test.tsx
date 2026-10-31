import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookTransformCard from "../src/components/webhook-transform-card";

const transforms = [
  {
    transform_id: "t1",
    webhook_id: "wh-1",
    field_mapping_count: 3,
    include_fields: null,
    exclude_fields: ["password", "token"],
    extra_header_count: 1,
  },
  {
    transform_id: "t2",
    webhook_id: "wh-2",
    field_mapping_count: 0,
    include_fields: ["id", "name"],
    exclude_fields: null,
    extra_header_count: 0,
  },
];

describe("WebhookTransformCard", () => {
  it("renders header", () => {
    const { container } = render(<WebhookTransformCard transforms={transforms} appName="My App" />);
    expect(container.textContent).toContain("Webhook Transforms");
  });

  it("shows transform count", () => {
    const { container } = render(<WebhookTransformCard transforms={transforms} appName="App" />);
    expect(container.textContent).toContain("2 transforms");
  });

  it("renders transform ids and webhook ids", () => {
    const { container } = render(<WebhookTransformCard transforms={transforms} appName="App" />);
    expect(container.textContent).toContain("t1");
    expect(container.textContent).toContain("wh-1");
  });

  it("shows mapping count", () => {
    const { container } = render(<WebhookTransformCard transforms={transforms} appName="App" />);
    expect(container.textContent).toContain("3 mappings");
  });

  it("shows include and exclude counts", () => {
    const { container } = render(<WebhookTransformCard transforms={transforms} appName="App" />);
    expect(container.textContent).toContain("2 excluded");
    expect(container.textContent).toContain("2 included");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookTransformCard transforms={[]} appName="App" />);
    expect(container.textContent).toContain("No transforms configured");
  });
});
