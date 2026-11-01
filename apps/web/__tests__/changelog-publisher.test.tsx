import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogPublisher } from "@/components/changelog-publisher";

describe("ChangelogPublisher", () => {
  it("renders publisher", () => {
    const { container } = render(
      <ChangelogPublisher version="3.0" summary="Major update" changeCount={5}
        availableChannels={["email", "slack"]} onPublish={vi.fn()}
        results={[
          { channel: "email", status: "delivered" },
          { channel: "slack", status: "delivered" },
        ]} />
    );
    expect(container.textContent).toContain("Publish v3.0");
    expect(container.textContent).toContain("Major update");
    expect(container.textContent).toContain("5 changes");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("delivered");
    expect(container.textContent).toContain("Publish All");
  });
});
