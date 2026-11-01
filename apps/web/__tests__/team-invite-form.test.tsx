import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeamInviteForm } from "@/components/team-invite-form";

describe("TeamInviteForm", () => {
  it("renders form", () => {
    const { container } = render(<TeamInviteForm orgName="Acme Corp" onInvite={vi.fn()} />);
    expect(container.textContent).toContain("Invite to Acme Corp");
    expect(container.textContent).toContain("Viewer");
    expect(container.textContent).toContain("Editor");
    expect(container.textContent).toContain("Admin");
    expect(container.textContent).toContain("Send Invite");
  });
});
