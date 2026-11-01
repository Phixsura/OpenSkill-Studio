import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplateCard from "../src/components/api-developer-api-api-developer-api-api-webhook-payload-transform-template-card";

const templates = [{ template_id: "t1", name: "Standard Event", variables: ["event_type", "source"], usage_count: 500 }];

describe("APIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplateCard", () => {
  it("shows templates", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplateCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("Transform Templates");
    expect(container.textContent).toContain("Standard Event");
    expect(container.textContent).toContain("{{event_type}}");
    expect(container.textContent).toContain("500 uses");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplateCard templates={[]} appName="App" />);
    expect(container.textContent).toContain("No templates");
  });
});
