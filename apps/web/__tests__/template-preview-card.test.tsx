import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TemplatePreviewCard from "../src/components/template-preview-card";

const templates = [
  {
    template_id: "welcome-email",
    content_type: "text/html",
    variable_count: 3,
    preview: "<h1>Hello {{name}}</h1>",
  },
  {
    template_id: "api-response",
    content_type: "application/json",
    variable_count: 2,
    preview: '{"status": "{{status}}"}',
  },
  {
    template_id: "notification",
    content_type: "text/plain",
    variable_count: 1,
    preview: "Your order {{id}} shipped",
  },
];

describe("TemplatePreviewCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<TemplatePreviewCard templates={templates} appName="My App" />);
    expect(container.textContent).toContain("Templates");
    expect(container.textContent).toContain("My App");
  });

  it("shows template count", () => {
    const { container } = render(<TemplatePreviewCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("3 templates");
  });

  it("renders template ids", () => {
    const { container } = render(<TemplatePreviewCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("welcome-email");
    expect(container.textContent).toContain("api-response");
  });

  it("shows content type badges", () => {
    const { container } = render(<TemplatePreviewCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("text/html");
    expect(container.textContent).toContain("application/json");
  });

  it("shows variable count", () => {
    const { container } = render(<TemplatePreviewCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("3 variables");
  });

  it("shows preview content", () => {
    const { container } = render(<TemplatePreviewCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("Hello {{name}}");
  });

  it("shows empty state", () => {
    const { container } = render(<TemplatePreviewCard templates={[]} appName="App" />);
    expect(container.textContent).toContain("No templates registered");
  });
});
