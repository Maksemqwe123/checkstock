/** Колонки как в макете — недели; в данных пока только «текущая». */
export function weekHeaders(count = 4): string[] {
  const now = new Date()
  const start = new Date(now)
  start.setDate(now.getDate() - ((now.getDay() + 6) % 7))
  return Array.from({ length: count }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i * 7)
    const year = d.getFullYear()
    const onejan = new Date(year, 0, 1)
    const week = Math.ceil(((d.getTime() - onejan.getTime()) / 86400000 + onejan.getDay() + 1) / 7)
    return `W${week} ${year}`
  })
}