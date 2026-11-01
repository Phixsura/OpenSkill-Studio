import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmailDigestPreview } from "@/components/email-digest-preview";

describe("EmailDigestPreview", () => {
  const sections = [
    { title: "📥 Installs", value: "150", change: 12.5 },
    { title: "💰 Revenue", value: "$2,500", change: -5 },
  ];
  it("renders", () => {
    const { container } = render(
      <EmailDigestPreview subject="Weekly" developerName="Alice" period="Oct 16-22"
        sections={sections} highlights={["Hit 1K installs!"]} />
    );
    expect(container.textContent).toContain("Hi Alice");
    expect(container.textContent).toContain("Oct 16-22");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("↑ 12.5%");
    expect(container.textContent).toContain("↓ 5%");
    expect(container.textContent).toContain("Hit 1K installs!");
  });
});
