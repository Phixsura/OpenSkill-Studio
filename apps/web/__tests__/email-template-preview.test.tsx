import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmailTemplatePreview } from "@/components/email-template-preview";

describe("EmailTemplatePreview", () => {
  it("renders email preview", () => {
    const { container } = render(
      <EmailTemplatePreview subject="Welcome to SuperApp!" preheader="Get started"
        bodyHtml="<p>Hello!</p>" templateId="welcome" />
    );
    expect(container.textContent).toContain("Welcome to SuperApp!");
    expect(container.textContent).toContain("Get started");
    expect(container.textContent).toContain("welcome");
    expect(container.querySelector("iframe")).toBeTruthy();
  });
});
