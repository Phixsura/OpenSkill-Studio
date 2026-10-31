import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotifHubPanel } from "@/components/notif-hub-panel";

describe("NotifHubPanel", () => {
  it("renders", () => {
    const { container } = render(
      <NotifHubPanel totalSent={5000} usersWithPrefs={200}
        byChannel={[
          { channel: "email", count: 3000 },
          { channel: "slack", count: 1500 },
          { channel: "webhook", count: 500 },
        ]} />
    );
    expect(container.textContent).toContain("Notification Hub");
    expect(container.textContent).toContain("5,000 sent");
    expect(container.textContent).toContain("200 users");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("3,000");
  });
});
