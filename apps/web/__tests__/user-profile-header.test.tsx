import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserProfileHeader } from "@/components/user-profile-header";

describe("UserProfileHeader", () => {
  it("renders profile", () => {
    const { container } = render(
      <UserProfileHeader name="Alice Chen" initials="AC" role="admin"
        plan="pro" joined="2024-01-15" org="Acme Corp"
        appCount={5} installsDisplay="80,000" badges={["verified", "top rated"]} />
    );
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("80,000 installs");
    expect(container.textContent).toContain("verified");
  });
});
