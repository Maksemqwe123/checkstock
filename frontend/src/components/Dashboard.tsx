import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchSnapshot } from '../api/client'
import type { Snapshot, ViewLevel } from '../api/types'
import {
  byFf,
  emptyTotals,
  metricRows,
  productsAtFf,
  sumBalances,
  totalsToCells,
} from '../lib/aggregate'
import { weekHeaders } from '../lib/weeks'

const COLS = weekHeaders()

export function Dashboard() {
  const [data, setData] = useState<Snapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [level, setLevel] = useState<ViewLevel>('ff')
  const [ffId, setFfId] = useState<string | null>(null)
  const [ffName, setFfName] = useState<string | null>(null)
  const [productId, setProductId] = useState<string | null>(null)
  const [productLabel, setProductLabel] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await fetchSnapshot())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const ffMap = useMemo(() => (data ? byFf(data) : new Map()), [data])

  const grandTotal = useMemo(() => {
    if (!data) return emptyTotals()
    const t = sumBalances(data.balances)
    t.inTransit = data.in_transit.reduce((s, x) => s + x.quantity, 0)
    return t
  }, [data])

  const productMap = useMemo(() => {
    if (!data || !ffId || !ffName) return new Map()
    return productsAtFf(data, ffId, ffName)
  }, [data, ffId, ffName])

  const skuTotals = useMemo(() => {
    if (!data || !ffId || !productId) return emptyTotals()
    const row = data.balances.find(
      (b) => b.fulfillment_center_id === ffId && b.product_id === productId,
    )
    if (!row) return emptyTotals()
    const t = {
      physical: row.physical,
      reserved: row.reserved_fbs,
      available: row.available,
      inTransit: 0,
    }
    if (ffName) {
      for (const tr of data.in_transit) {
        if (tr.sku === row.sku && (tr.from_ff === ffName || tr.to_ff === ffName)) {
          t.inTransit += tr.quantity
        }
      }
    }
    return t
  }, [data, ffId, ffName, productId])

  const pickFf = (id: string, name: string) => {
    setFfId(id)
    setFfName(name)
    setProductId(null)
    setProductLabel(null)
    setLevel('product')
  }

  const pickProduct = (id: string, label: string) => {
    setProductId(id)
    setProductLabel(label)
    setLevel('sku')
  }

  const firstFf = useMemo(() => {
    const rows = [...ffMap.values()].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    return rows[0] ?? null
  }, [ffMap])

  const resolveFf = (): { id: string; name: string } | null => {
    if (ffId && ffName) return { id: ffId, name: ffName }
    if (!firstFf) return null
    setFfId(firstFf.id)
    setFfName(firstFf.name)
    return { id: firstFf.id, name: firstFf.name }
  }

  const resolveProduct = (): { id: string; label: string } | null => {
    const ff = resolveFf()
    if (!ff || !data) return null
    if (productId && productLabel) return { id: productId, label: productLabel }
    const rows = [...productsAtFf(data, ff.id, ff.name).values()].sort((a, b) =>
      a.sku.localeCompare(b.sku),
    )
    const first = rows[0]
    if (!first) return null
    const label = `${first.sku} — ${first.name}`
    setProductId(first.productId)
    setProductLabel(label)
    return { id: first.productId, label }
  }

  const setLevelSafe = (next: ViewLevel) => {
    if (next === 'ff') {
      setLevel('ff')
      setFfId(null)
      setFfName(null)
      setProductId(null)
      setProductLabel(null)
      return
    }
    if (next === 'product') {
      if (!resolveFf()) return
      setLevel('product')
      setProductId(null)
      setProductLabel(null)
      return
    }
    if (next === 'sku') {
      if (!resolveProduct()) return
      setLevel('sku')
    }
  }

  const crumb = (
    <div className="crumb">
      <button type="button" className="link" onClick={() => setLevelSafe('ff')}>
        Все ФФ
      </button>
      {ffName && (
        <>
          {' '}
          ›{' '}
          <button type="button" className="link" onClick={() => setLevelSafe('product')}>
            {ffName}
          </button>
        </>
      )}
      {productLabel && (
        <>
          {' '}
          › <strong>{productLabel}</strong>
        </>
      )}
    </div>
  )

  let body: ReactNode
  if (loading) {
    body = <p className="status">Загрузка…</p>
  } else if (error) {
    body = (
      <p className="status error">
        {error}. Проверьте, что API запущен (docker compose / poetry run app).
      </p>
    )
  } else if (level === 'ff') {
    const rows = [...ffMap.values()].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    body = (
      <table className="grid">
        <thead>
          <tr>
            <th>ФФ</th>
            {COLS.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="clickable" onClick={() => pickFf(r.id, r.name)}>
              <td>{r.name}</td>
              {totalsToCells(r.totals).map((v, i) => (
                <td key={i}>{v}</td>
              ))}
            </tr>
          ))}
          <tr className="total">
            <td>Итого по сети</td>
            {totalsToCells(grandTotal).map((v, i) => (
              <td key={i}>{v}</td>
            ))}
          </tr>
        </tbody>
      </table>
    )
  } else if (level === 'product' && ffId && ffName) {
    const rows = [...productMap.values()].sort((a, b) => a.sku.localeCompare(b.sku))
    const shopTotal = rows.reduce(
      (acc, r) => ({
        physical: acc.physical + r.physical,
        reserved: acc.reserved + r.reserved,
        available: acc.available + r.available,
        inTransit: acc.inTransit + r.inTransit,
      }),
      emptyTotals(),
    )
    body = (
      <table className="grid">
        <thead>
          <tr>
            <th>Товар</th>
            {COLS.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr
              key={r.productId}
              className="clickable"
              onClick={() => pickProduct(r.productId, `${r.sku} — ${r.name}`)}
            >
              <td>
                <span className="sku">{r.sku}</span> {r.name}
              </td>
              {totalsToCells(r).map((v, i) => (
                <td key={i}>{v}</td>
              ))}
            </tr>
          ))}
          <tr className="total">
            <td>Итого по ФФ</td>
            {totalsToCells(shopTotal).map((v, i) => (
              <td key={i}>{v}</td>
            ))}
          </tr>
        </tbody>
      </table>
    )
  } else if (level === 'sku' && productLabel) {
    const rows = metricRows(skuTotals)
    body = (
      <>
        <p className="sku-head">
          SKU: <strong>{productLabel}</strong>
        </p>
        <table className="grid">
          <thead>
            <tr>
              <th>Показатель</th>
              {COLS.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <td>{row.label}</td>
                {row.values.map((v, i) => (
                  <td key={i}>{v}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </>
    )
  } else {
    body = <p className="status">Выберите уровень слева или кликните по строке в таблице.</p>
  }

  return (
    <main className="page">
      <header className="topline">
        <div>
          <h1>Где сейчас товар?</h1>
          <p className="sub">Три уровня: ФФ → товары → артикул (как на макете, без дерева)</p>
        </div>
        <a
          href={
            (import.meta.env.VITE_API_URL ?? '/api').replace(/\/$/, '') === '/api'
              ? '/docs'
              : `${(import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:4005').replace(/\/$/, '')}/docs`
          }
          target="_blank"
          rel="noreferrer"
        >
          OpenAPI
        </a>
      </header>

      <section className="panel">
        <div className="panel-head">
          <h2>Уровень просмотра</h2>
          <p>
            Колонки — недели; в первой колонке — факт из API. Клик по <strong>Север</strong> /{' '}
            <strong>Юг</strong> или вкладка «Товары».
          </p>
          <div className="tabs" role="tablist">
            <button
              type="button"
              role="tab"
              className={`tab ${level === 'ff' ? 'active' : ''}`}
              onClick={() => setLevelSafe('ff')}
            >
              ФФ
            </button>
            <button
              type="button"
              role="tab"
              className={`tab ${level === 'product' ? 'active' : ''}`}
              disabled={!data || ffMap.size === 0}
              onClick={() => setLevelSafe('product')}
            >
              Товары
            </button>
            <button
              type="button"
              role="tab"
              className={`tab ${level === 'sku' ? 'active' : ''}`}
              disabled={!data || ffMap.size === 0}
              onClick={() => setLevelSafe('sku')}
            >
              Артикул
            </button>
          </div>
        </div>
        {crumb}
        <div className="grid-wrap">{body}</div>
      </section>

      <p className="legend">
        ФФ = «магазины», товары = «категории» по выбранному складу. Данные: GET /inventory/snapshot.
        <button type="button" className="link inline" onClick={() => void load()}>
          Обновить
        </button>
      </p>
    </main>
  )
}