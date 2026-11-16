import type { BalanceRow, Snapshot, TransitRow } from '../api/types'

export interface MetricTotals {
  physical: number
  reserved: number
  available: number
  inTransit: number
}

export function emptyTotals(): MetricTotals {
  return { physical: 0, reserved: 0, available: 0, inTransit: 0 }
}

export function sumBalances(rows: BalanceRow[]): MetricTotals {
  return rows.reduce(
    (acc, r) => ({
      physical: acc.physical + r.physical,
      reserved: acc.reserved + r.reserved_fbs,
      available: acc.available + r.available,
      inTransit: acc.inTransit,
    }),
    emptyTotals(),
  )
}

export function transitForFf(transit: TransitRow[], ffName: string): number {
  return transit.reduce((s, t) => {
    if (t.from_ff === ffName || t.to_ff === ffName) {
      return s + t.quantity
    }
    return s
  }, 0)
}

export function byFf(snapshot: Snapshot): Map<string, { id: string; name: string; active: boolean; totals: MetricTotals }> {
  const map = new Map<string, { id: string; name: string; active: boolean; totals: MetricTotals }>()
  for (const row of snapshot.balances) {
    const cur = map.get(row.fulfillment_center_id)
    if (!cur) {
      map.set(row.fulfillment_center_id, {
        id: row.fulfillment_center_id,
        name: row.fulfillment_center_name,
        active: row.ff_active,
        totals: emptyTotals(),
      })
    }
    const entry = map.get(row.fulfillment_center_id)!
    entry.totals.physical += row.physical
    entry.totals.reserved += row.reserved_fbs
    entry.totals.available += row.available
  }
  for (const entry of map.values()) {
    entry.totals.inTransit = transitForFf(snapshot.in_transit, entry.name)
  }
  return map
}

export function productsAtFf(snapshot: Snapshot, ffId: string, ffName: string): Map<string, MetricTotals & { sku: string; name: string; productId: string }> {
  const map = new Map<string, MetricTotals & { sku: string; name: string; productId: string }>()
  for (const row of snapshot.balances.filter((b) => b.fulfillment_center_id === ffId)) {
    map.set(row.product_id, {
      productId: row.product_id,
      sku: row.sku,
      name: row.product_name,
      physical: row.physical,
      reserved: row.reserved_fbs,
      available: row.available,
      inTransit: 0,
    })
  }
  for (const t of snapshot.in_transit.filter((t) => t.from_ff === ffName || t.to_ff === ffName)) {
    for (const row of snapshot.balances) {
      if (row.sku === t.sku && row.fulfillment_center_id === ffId) {
        const p = map.get(row.product_id)
        if (p) {
          p.inTransit += t.quantity
        }
      }
    }
  }
  return map
}

/** Строки метрик × недели: значение только в первой колонке (остальные — 0 / план). */
export function metricRows(t: MetricTotals): { label: string; values: number[] }[] {
  const z = [t.physical, t.reserved, t.available, t.inTransit]
  return [
    { label: 'Физический остаток', values: [z[0], 0, 0, 0] },
    { label: 'Резерв FBS', values: [z[1], 0, 0, 0] },
    { label: 'Доступно', values: [z[2], 0, 0, 0] },
    { label: 'В пути', values: [z[3], 0, 0, 0] },
  ]
}

export function totalsToCells(t: MetricTotals): number[] {
  return [t.physical, t.reserved, t.available, t.inTransit]
}