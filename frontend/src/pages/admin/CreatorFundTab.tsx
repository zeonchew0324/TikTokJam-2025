import { useEffect, useMemo, useState } from 'react'
import { mockApiService } from '../../services/mockApiService'
import type { Category } from '../../types/admin'

export function CreatorFundTab() {
  const [categories, setCategories] = useState<Category[]>([])
  const [amount, setAmount] = useState<string>('100000')

  useEffect(() => {
    mockApiService.getVideoCategories().then(setCategories)
  }, [])

  // Retrieve value from backend
  // EXPECT: total fund 
  // useEffect(() => {
  //   fetch("/api/getValue") // adjust endpoint
  //     .then((res) => res.json())
  //     .then((data) => setAmount(data.value)) 
  //     .catch((err) => console.error(err));
  // }, []);

  //Retrieve categories and popularity 
  // EXPECT: category name, popularity percentage
  // useEffect(() => {
  //   fetch("/api/video-categories") // adjust endpoint
  //     .then((res) => res.json())
  //     .then((data: Category[]) => {
  //       setCategories(data)
  //     })
  //     .catch((err) => {
  //       console.error("Failed to load categories:", err)
  //     })
  // }, []);

  const total = useMemo(() => Number(amount || 0), [amount])

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 16, color: '#fff', fontFamily: 'sans-serif', padding: 20, background: '#000' }}>
      <div>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Fund Allocation </div>
        <div style={{ background: '#121212', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 12, padding: 12 }}>
          <label style={{ display: 'block', color: 'rgba(255,255,255,0.8)', marginBottom: 8 }}>
            Total Fund Amount ($)
          </label>
          <div
            style={{
              width: '100%',
              padding: '8px 10px',
              borderRadius: 8,
              border: '1px solid rgba(255,255,255,0.2)',
              background: '#0f0f0f',
              color: '#fff',
              boxSizing: 'border-box'  // Add this line
            }}
          > { amount || "Loading..." }
          </div>
        </div>
      </div>
      <div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16 }}>
          <div>
            <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Category Popularity & Distribution</div>
            <div style={{ overflowX: 'auto', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#181818', textAlign: 'left' }}>
                    <th style={{ padding: 12 }}>Category</th>
                    <th style={{ padding: 12 }}>Popularity %</th>
                    <th style={{ padding: 12 }}>Allocated Fund ($)</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map(c => (
                    <tr key={c.categoryId} style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                      <td style={{ padding: 12 }}>{c.name}</td>
                      <td style={{ padding: 12 }}>{c.popularityPercentage.toFixed(1)}%</td>
                      <td style={{ padding: 12 }}>{((c.popularityPercentage / 100) * total).toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                    </tr>
                  ))}
                  {categories.length === 0 && (
                    <tr>
                      <td colSpan={3} style={{ padding: 16, color: 'rgba(255,255,255,0.6)', textAlign: 'center' }}>Loading Categories...</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          <div>
            <PieChart categories={categories} />
          </div>
        </div>
      </div>
    </div>
  )
}

function PieChart(props: { categories: Category[] }) {
  const { categories } = props;
  const total = categories.reduce((sum, c) => sum + c.popularityPercentage, 0);
  let cumulative = 0;
  
  // Increased size for a bigger chart
  const width = 340;
  const height = 340;
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) / 2 - 20; // Radius calculated from size

  // New vibrant color palette for dark mode, inspired by TikTok
  const colors = [
    '#FE2C55', '#25F4EE', '#F7B500', '#A450E6', '#40D8A0', 
    '#FF69B4', '#58A6FF', '#FF8C00', '#ADFF2F', '#DA70D6', 
    '#00CED1', '#FF4500'
  ];

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ background: '#111', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }}>
      {categories.map((c, idx) => {
        // Angles are adjusted by -PI/2 to start from the top (12 o'clock)
        const startAngle = (cumulative / total) * 2 * Math.PI - Math.PI / 2;
        cumulative += c.popularityPercentage;
        const endAngle = (cumulative / total) * 2 * Math.PI - Math.PI / 2;
        
        const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;
        
        const x1 = cx + radius * Math.cos(startAngle);
        const y1 = cy + radius * Math.sin(startAngle);
        const x2 = cx + radius * Math.cos(endAngle);
        const y2 = cy + radius * Math.sin(endAngle);
        
        const d = `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
        
        return <path key={c.categoryId} d={d} fill={colors[idx % colors.length]} />;
      })}
      <text x={cx} y={cy} dominantBaseline="middle" textAnchor="middle" fill="#fff" style={{ fontSize: '18px', fontWeight: 600 }}>Popularity</text>
    </svg>
  );
}
