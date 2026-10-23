import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmailTemplatePreview } from "@/components/email-template-preview";

describe("EmailTemplatePreview", () => {
  const templates = [
    { id: "welcome", name: "Welcome", subject: "Welcome to {{app_name}}!", variables: ["app_name", "user_name"] },
  ];
  it("renders", () => {
    const { container } = render(
      <EmailTemplatePreview templates={templates} onPreview={vi.fn(() => "")} onSend={vi.fn()} />
    );
    expect(container.textContent).toContain("Email Templates");
    expect(container.textContent).toContain("Welcome");
    expect(container.textContent).toContain("{{app_name}}");
    expect(container.textContent).toContain("{{user_name}}");
  });
  it("send test", () => {
    const fn = vi.fn();
    const { container } = render(
      <EmailTemplatePreview templates={templates} onPreview={vi.fn(() => "")} onSend={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Send Test Email")!);
    expect(fn).toHaveBeenCalledWith("welcome");
  });
});
