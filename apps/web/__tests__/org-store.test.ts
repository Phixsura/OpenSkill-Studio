import { beforeEach, describe, expect, it } from "vitest";

import { useOrgStore } from "@/stores/org";

describe("org store", () => {
  beforeEach(() => {
    useOrgStore.getState().clearOrg();
  });

  it("should start with no org selected", () => {
    const state = useOrgStore.getState();
    expect(state.currentOrgId).toBeNull();
    expect(state.currentOrg).toBeNull();
  });

  it("should set current org", () => {
    const org = {
      id: "01JK",
      name: "Test Org",
      slug: "test-org",
      description: null,
      logo_url: null,
      role: "owner",
      member_count: 1,
      created_at: "2026-01-01T00:00:00Z",
    };

    useOrgStore.getState().setCurrentOrg(org);

    const state = useOrgStore.getState();
    expect(state.currentOrgId).toBe("01JK");
    expect(state.currentOrg?.name).toBe("Test Org");
  });

  it("should clear org", () => {
    useOrgStore.getState().setCurrentOrg({
      id: "01JK",
      name: "Test",
      slug: "test",
      description: null,
      logo_url: null,
      role: "owner",
      member_count: 1,
      created_at: "2026-01-01T00:00:00Z",
    });

    useOrgStore.getState().clearOrg();

    const state = useOrgStore.getState();
    expect(state.currentOrgId).toBeNull();
    expect(state.currentOrg).toBeNull();
  });
});
