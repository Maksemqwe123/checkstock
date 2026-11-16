export interface BalanceRow {
  sku: string
  product_name: string
  product_id: string
  fulfillment_center_id: string
  fulfillment_center_name: string
  ff_active: boolean
  physical: number
  reserved_fbs: number
  available: number
}

export interface TransitRow {
  sku: string
  quantity: number
  kind: string
  from_ff: string
  to_ff: string
}

export interface Snapshot {
  balances: BalanceRow[]
  in_transit: TransitRow[]
}

export type ViewLevel = 'ff' | 'product' | 'sku'