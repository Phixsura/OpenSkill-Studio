import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperProfileCard from "../src/components/api-developer-profile-card";

const profiles = [{ developer_id: "alice", display_name: "Alice Smith", email: "alice@dev.com", bio: "Dev", app_count: 3, api_key_count: 2 }];

describe("APIDeveloperProfileCard", () => {
  it("shows profiles", () => {
    const { container } = render(<APIDeveloperProfileCard profiles={profiles} appName="App" />);
    expect(container.textContent).toContain("Developer Profiles");
    expect(container.textContent).toContain("Alice Smith");
    expect(container.textContent).toContain("3 apps");
    expect(container.textContent).toContain("alice@dev.com");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperProfileCard profiles={[]} appName="App" />);
    expect(container.textContent).toContain("No developer profiles");
  });
});
