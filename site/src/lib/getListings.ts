import { getCollection } from "astro:content";
import { DEFAULT_STATUS, STATUS_ORDER, type Status } from "./status";

// Directory sorting: by status first (active, inactive, closed), then featured items.
export function sortListings<
  T extends { data: { status?: string; featured?: boolean } },
>(listings: Array<T>): Array<T> {
  const rank = (status?: string) =>
    STATUS_ORDER[(status ?? DEFAULT_STATUS) as Status] ?? 0;

  return [...listings].sort(
    (a, b) =>
      rank(a.data.status) - rank(b.data.status) ||
      Number(b.data.featured) - Number(a.data.featured),
  );
}

export async function getListings() {
  return sortListings(await getCollection("directory"));
}
