import { useEffect, useMemo, useState } from 'react'
import { fetchVideoRevenueMock, type CategorySegment, type RevenueResponse } from './mockRevenue'

export function VideoAnalyticsPage(props: { videoId: string; onBack: () => void }) {
  const { videoId, onBack } = props
  const [data, setData] = useState<RevenueResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<'education' | 'cooking' | 'entertainment'>('education')

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      try {
        const json = await fetchVideoRevenueMock(videoId)
        if (!cancelled) {
          setData(json)
          setSelected(json.categories[0]?.categoryId ?? 'education')
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? 'Failed to load analytics')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [videoId])

  const selectedLevel = useMemo(() => data?.categories.find(c => c.categoryId === selected) ?? null, [data, selected])

  if (loading) return <div>Loading analytics…</div>
  if (error) return <div style={{ color: 'tomato' }}>Error: {error}</div>
  if (!data) return null

  return (
    <div>
      <button
        onClick={onBack}
        aria-label="Back"
        style={{
          marginBottom: 12,
          background: 'none',
          border: 'none',
          color: '#fff',
          cursor: 'pointer',
          padding: 4
        }}
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
        </svg>
      </button>
      <h2>Video Analytics</h2>
      <div style={{ opacity: 0.85, marginBottom: 8 }}>Total Engagement: {data.totalEngagementScore.toLocaleString()}</div>
      <div style={{ display: 'grid', gridTemplateRows: '1fr 1fr', gap: 16, height: '70vh' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
          <CylinderChart
            categories={data.categories}
            selected={selected}
            onSelect={setSelected}
          />
        </div>
        <div style={{ padding: 16, borderRadius: 12, border: '1px solid rgba(255,255,255,0.12)' }}>
          {selectedLevel && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ fontWeight: 700, fontSize: 18 }}>{selectedLevel.name}</div>
              <div>Total Revenue: ${selectedLevel.totalRevenue.toFixed(2)}</div>
              <div>Engagement Score: {selectedLevel.engagementScore}</div>
              <div>Rank: Top {Math.max(1, selectedLevel.rankPercent)}%</div>
              <div>Tier: {selectedLevel.tier}</div>
              {selectedLevel.nextTierRequirement === null ? (
                <div>Next Tier Requirement: —</div>
              ) : (
                <div>Next Tier Requirement: +{selectedLevel.nextTierRequirement} engagement</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function CylinderChart(props: {
  categories: CategorySegment[];
  selected: 'education' | 'cooking' | 'entertainment';
  onSelect: (l: 'education' | 'cooking' | 'entertainment') => void;
}) {
  const { categories, selected, onSelect } = props;

  const colorFor = (id: 'education' | 'cooking' | 'entertainment') =>
    id === 'education' ? '#1677ff' : id === 'cooking' ? '#fa8c16' : '#13c2c2';
  const colorForSelected = (id: 'education' | 'cooking' | 'entertainment') =>
    id === 'education' ? '#4096ff' : id === 'cooking' ? '#ffa940' : '#36cfc9';

  return (
    // Main container for the chart
    <div style={{ width: 180, height: 320, display: 'flex', flexDirection: 'column-reverse' }}>
      {categories.map((cat) => {
        const isSelected = selected === cat.categoryId;
        const baseColor = colorFor(cat.categoryId);
        const fillColor = isSelected ? colorForSelected(cat.categoryId) : baseColor;

        return (
          // Wrapper for each segment, height is now proportional to its value
          <div
            key={cat.categoryId}
            style={{
              position: 'relative',
              height: `${cat.percentContribution}%`,
              // No vertical margin to make the cylinders stack seamlessly
              margin: '0',
            }}
          >
            {/* The clickable element and main body of the cylinder segment */}
            <div
              onClick={() => onSelect(cat.categoryId)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelect(cat.categoryId)}
              title={`${cat.name} • ${cat.percentContribution}%`}
              style={{
                position: 'relative',
                width: '100%',
                height: '100%',
                background: fillColor,
                cursor: 'pointer',
                transition: 'background-color 180ms ease, transform 180ms ease',
                boxShadow: 'inset 0 -6px 12px rgba(0,0,0,0.25)',
              }}
            >
              {/* Top ellipse of the cylinder */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: 30, // The "thickness" of the cylinder cap
                  background: fillColor,
                  borderRadius: '50%',
                  transform: 'translateY(-50%)',
                  filter: 'brightness(1.15)', // Make the top appear lit
                }}
              />
              {/* Bottom ellipse of the cylinder */}
              <div
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  width: '100%',
                  height: 30, // The "thickness" of the cylinder base
                  background: fillColor,
                  borderRadius: '50%',
                  transform: 'translateY(50%)',
                  filter: 'brightness(0.75)', // Make the bottom appear shadowed
                }}
              />
            </div>

            {/* Tooltip for the selected segment */}
            {isSelected && (
              <div style={{
                position: 'absolute', right: -220, top: '50%', transform: 'translateY(-50%)',
                background: 'rgba(0,0,0,0.85)', color: 'white', padding: '8px 12px', borderRadius: 8,
                border: '1px solid rgba(255,255,255,0.08)', zIndex: 10
              }}>
                <div style={{ fontWeight: 700 }}>{cat.name}</div>
                <div>Contribution: {cat.percentContribution}%</div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}


