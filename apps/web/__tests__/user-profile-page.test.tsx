import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserProfilePage } from "@/components/user-profile-page";

describe("UserProfilePage", () => {
  it("renders profile", () => {
    const { container } = render(
      <UserProfilePage name="Alice Chen" email="alice@x.com" avatarUrl="https://img.com/a.png"
        bio="Builder" role="developer" memberSince="2024-01-01"
        stats={{ apps: 3, totalInstalls: 15000, activityCount: 150 }}
        recentApps={[{ id: "a1", name: "SuperApp", icon: "🚀" }]} onSelectApp={vi.fn()} />
    );
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("Builder");
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("SuperApp");
  });
});
