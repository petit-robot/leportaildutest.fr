// Status of a directory resource. Values are internal identifiers;
// the displayed labels come from the theme settings ([directoryUI.status]).
export const STATUSES = ["active", "inactive", "closed"] as const;

export type Status = (typeof STATUSES)[number];

export const DEFAULT_STATUS: Status = "active";

// Sort order: active resources first.
export const STATUS_ORDER: Record<Status, number> = {
  active: 0,
  inactive: 1,
  closed: 2,
};

// A resource that is no longer active is greyed out.
export function isDimmedStatus(status?: string): boolean {
  return Boolean(status) && status !== DEFAULT_STATUS;
}