import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UserPreferenceCard from "../src/components/user-preference-card";

const prefs = [
  { key: "theme", value: "dark", is_default: false, description: "UI theme" },
  { key: "language", value: "en", is_default: true, description: "Display language" },
  { key: "notifications", value: true, is_default: true, description: "" },
];

describe("UserPreferenceCard", () => {
  it("renders header with user id", () => {
    const { container } = render(
      <UserPreferenceCard preferences={prefs} userId="user-42" appName="My App" />,
    );
    expect(container.textContent).toContain("Preferences");
    expect(container.textContent).toContain("user-42");
  });

  it("shows customized count", () => {
    const { container } = render(
      <UserPreferenceCard preferences={prefs} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("1 customized");
  });

  it("renders preference keys with spaces", () => {
    const { container } = render(
      <UserPreferenceCard preferences={prefs} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("language");
  });

  it("shows values", () => {
    const { container } = render(
      <UserPreferenceCard preferences={prefs} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("On"); // true → On
  });

  it("shows default label", () => {
    const { container } = render(
      <UserPreferenceCard preferences={prefs} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("default");
  });

  it("shows description", () => {
    const { container } = render(
      <UserPreferenceCard preferences={prefs} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("UI theme");
  });

  it("shows empty state", () => {
    const { container } = render(<UserPreferenceCard preferences={[]} userId="u1" appName="App" />);
    expect(container.textContent).toContain("No preferences");
  });
});
