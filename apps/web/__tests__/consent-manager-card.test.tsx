import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConsentManagerCard from "../src/components/consent-manager-card";

const consents = [
  {
    purpose: "analytics",
    granted: true,
    last_updated: new Date(Date.now() - 86_400_000).toISOString(),
  },
  {
    purpose: "marketing_emails",
    granted: false,
    last_updated: new Date(Date.now() - 3_600_000).toISOString(),
  },
  {
    purpose: "data_sharing",
    granted: true,
    last_updated: new Date(Date.now() - 7_200_000).toISOString(),
  },
];

describe("ConsentManagerCard", () => {
  it("renders header with user id", () => {
    const { container } = render(
      <ConsentManagerCard consents={consents} userId="user-42" appName="My App" />,
    );
    expect(container.textContent).toContain("Consent");
    expect(container.textContent).toContain("user-42");
  });

  it("shows granted count", () => {
    const { container } = render(
      <ConsentManagerCard consents={consents} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("2/3 granted");
  });

  it("renders purpose names with spaces", () => {
    const { container } = render(
      <ConsentManagerCard consents={consents} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("marketing emails");
    expect(container.textContent).toContain("data sharing");
  });

  it("shows granted and withdrawn labels", () => {
    const { container } = render(
      <ConsentManagerCard consents={consents} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("Granted");
    expect(container.textContent).toContain("Withdrawn");
  });

  it("shows updated time", () => {
    const { container } = render(
      <ConsentManagerCard consents={consents} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("Updated");
  });

  it("shows empty state", () => {
    const { container } = render(<ConsentManagerCard consents={[]} userId="u1" appName="App" />);
    expect(container.textContent).toContain("No consent records");
  });
});
