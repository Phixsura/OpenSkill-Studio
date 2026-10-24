import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SupportContactCard } from "@/components/support-contact-card";

describe("SupportContactCard", () => {
  it("renders support", () => {
    const { container } = render(
      <SupportContactCard developer="Acme Corp" responseTime="4 hours"
        docsUrl="https://docs.acme.com"
        channels={[
          { type: "email", icon: "📧", value: "help@acme.com" },
          { type: "discord", icon: "💬", value: "Discord Community" },
        ]} />
    );
    expect(container.textContent).toContain("Support");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("4 hours");
    expect(container.textContent).toContain("help@acme.com");
    expect(container.textContent).toContain("Discord Community");
    expect(container.textContent).toContain("View Documentation");
  });
});
