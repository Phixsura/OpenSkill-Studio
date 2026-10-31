import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EmailTemplateCard from "../src/components/email-template-card";

const templates = [
  {
    template_id: "welcome",
    name: "Welcome Email",
    subject: "Welcome {{name}}!",
    variable_count: 2,
    has_plain_text: true,
  },
  {
    template_id: "reset",
    name: "Password Reset",
    subject: "Reset your password",
    variable_count: 1,
    has_plain_text: false,
  },
];

describe("EmailTemplateCard", () => {
  it("renders header", () => {
    const { container } = render(<EmailTemplateCard templates={templates} appName="My App" />);
    expect(container.textContent).toContain("Email Templates");
  });

  it("shows template count", () => {
    const { container } = render(<EmailTemplateCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("2 templates");
  });

  it("renders names and subjects", () => {
    const { container } = render(<EmailTemplateCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("Welcome Email");
    expect(container.textContent).toContain("Welcome {{name}}!");
  });

  it("shows variable count", () => {
    const { container } = render(<EmailTemplateCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("2 vars");
  });

  it("shows plain text badge", () => {
    const { container } = render(<EmailTemplateCard templates={templates} appName="App" />);
    expect(container.textContent).toContain("+ plain text");
  });

  it("shows empty state", () => {
    const { container } = render(<EmailTemplateCard templates={[]} appName="App" />);
    expect(container.textContent).toContain("No email templates");
  });
});
