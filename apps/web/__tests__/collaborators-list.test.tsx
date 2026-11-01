import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CollaboratorsList } from "@/components/collaborators-list";

describe("CollaboratorsList", () => {
  const collabs = [
    { id: "u1", name: "Alice", email: "a@b.com", role: "owner", roleIcon: "👑", canDeploy: true, canPublish: true },
    { id: "u2", name: "Bob", email: "b@b.com", role: "contributor", roleIcon: "✏️", canDeploy: false, canPublish: false },
  ];
  it("renders collaborators", () => {
    const { container } = render(
      <CollaboratorsList collaborators={collabs} appName="SuperApp" onRemove={vi.fn()} onInvite={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp Collaborators");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("Bob");
    expect(container.textContent).toContain("+ Invite");
  });
});
