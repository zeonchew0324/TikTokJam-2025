import { useEffect, useMemo, useState, useRef } from 'react'
import * as THREE from 'three'

// Types
interface Category {
  categoryId: string;
  name: string;
  popularityPercentage: number;
}

interface ClusteringData {
  dataPoints: number[][];
  centroids: number[][];
}

// Mock API service for clustering data
const clusteringApiService = {
  async getClusteringData(): Promise<ClusteringData> {
    // TODO: Replace with actual API call when server is available
    // const response = await fetch('/api/clustering-data');
    // const data = await response.json();
    // return data;
    
    // Mock data for demonstration
    const dataPoints = [];
    const centroids = [];
    
    // Generate 100 random data points in 3 clusters
    for (let i = 0; i < 100; i++) {
      const cluster = Math.floor(Math.random() * 3);
      const baseX = cluster === 0 ? -2 : cluster === 1 ? 2 : 0;
      const baseY = cluster === 0 ? -2 : cluster === 1 ? 2 : -3;
      const baseZ = cluster === 0 ? 1 : cluster === 1 ? -1 : 2;
      
      dataPoints.push([
        baseX + (Math.random() - 0.5) * 2,
        baseY + (Math.random() - 0.5) * 2,
        baseZ + (Math.random() - 0.5) * 2
      ]);
    }
    
    // Generate 3 centroids
    centroids.push([-2, -2, 1]);
    centroids.push([2, 2, -1]);
    centroids.push([0, -3, 2]);
    
    return { dataPoints, centroids };
  }
};

// Mock API service (existing)
const mockApiService = {
  async getVideoCategories(): Promise<Category[]> {
    return [
      { categoryId: '1', name: 'Gaming', popularityPercentage: 25.5 },
      { categoryId: '2', name: 'Music', popularityPercentage: 22.3 },
      { categoryId: '3', name: 'Comedy', popularityPercentage: 18.7 },
      { categoryId: '4', name: 'Education', popularityPercentage: 15.2 },
      { categoryId: '5', name: 'Food', popularityPercentage: 12.1 },
      { categoryId: '6', name: 'Travel', popularityPercentage: 6.2 }
    ];
  }
};

function ThreeJSClusterPlot({ dataPoints, centroids }: { dataPoints: number[][], centroids: number[][] }) {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!mountRef.current || !dataPoints.length) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(8, 8, 8);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;
    mountRef.current.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Create data points
    const dataPointsGroup = new THREE.Group();
    const pointGeometry = new THREE.SphereGeometry(0.05, 8, 8);
    
    dataPoints.forEach((point, index) => {
      // Color points based on closest centroid
      let closestCentroid = 0;
      let minDistance = Infinity;
      
      centroids.forEach((centroid, centroidIndex) => {
        const distance = Math.sqrt(
          Math.pow(point[0] - centroid[0], 2) +
          Math.pow(point[1] - centroid[1], 2) +
          Math.pow(point[2] - centroid[2], 2)
        );
        if (distance < minDistance) {
          minDistance = distance;
          closestCentroid = centroidIndex;
        }
      });

      const colors = [0xFE2C55, 0x25F4EE, 0xF7B500];
      const pointMaterial = new THREE.MeshLambertMaterial({ 
        color: colors[closestCentroid % colors.length],
        transparent: true,
        opacity: 0.8
      });
      
      const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);
      pointMesh.position.set(point[0], point[1], point[2]);
      pointMesh.castShadow = true;
      dataPointsGroup.add(pointMesh);
    });

    scene.add(dataPointsGroup);

    // Create centroids
    const centroidsGroup = new THREE.Group();
    const centroidGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    
    centroids.forEach((centroid, index) => {
      const colors = [0xFE2C55, 0x25F4EE, 0xF7B500];
      const centroidMaterial = new THREE.MeshLambertMaterial({ 
        color: colors[index % colors.length],
        emissive: colors[index % colors.length],
        emissiveIntensity: 0.3
      });
      
      const centroidMesh = new THREE.Mesh(centroidGeometry, centroidMaterial);
      centroidMesh.position.set(centroid[0], centroid[1], centroid[2]);
      centroidMesh.castShadow = true;
      centroidsGroup.add(centroidMesh);

      // Add a subtle glow effect
      const glowGeometry = new THREE.SphereGeometry(0.2, 16, 16);
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: colors[index % colors.length],
        transparent: true,
        opacity: 0.2
      });
      const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
      glowMesh.position.set(centroid[0], centroid[1], centroid[2]);
      centroidsGroup.add(glowMesh);
    });

    scene.add(centroidsGroup);

    // Add coordinate axes
    const axesHelper = new THREE.AxesHelper(3);
    scene.add(axesHelper);

    // Add grid
    const gridHelper = new THREE.GridHelper(10, 10, 0x333333, 0x333333);
    scene.add(gridHelper);

    // Mouse controls for rotation
    let isMouseDown = false;
    let mouseX = 0;
    let mouseY = 0;
    let targetRotationX = 0;
    let targetRotationY = 0;
    let rotationX = 0;
    let rotationY = 0;

    const handleMouseDown = (event: MouseEvent) => {
      isMouseDown = true;
      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const handleMouseUp = () => {
      isMouseDown = false;
    };

    const handleMouseMove = (event: MouseEvent) => {
      if (!isMouseDown) return;

      const deltaX = event.clientX - mouseX;
      const deltaY = event.clientY - mouseY;

      targetRotationY += deltaX * 0.01;
      targetRotationX += deltaY * 0.01;

      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const handleWheel = (event: WheelEvent) => {
      event.preventDefault();
      const scale = event.deltaY > 0 ? 1.1 : 0.9;
      camera.position.multiplyScalar(scale);
    };

    renderer.domElement.addEventListener('mousedown', handleMouseDown);
    renderer.domElement.addEventListener('mouseup', handleMouseUp);
    renderer.domElement.addEventListener('mousemove', handleMouseMove);
    renderer.domElement.addEventListener('wheel', handleWheel);

    // Animation loop
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);

      // Smooth rotation interpolation
      rotationX += (targetRotationX - rotationX) * 0.05;
      rotationY += (targetRotationY - rotationY) * 0.05;

      // Apply rotation around the origin
      const radius = camera.position.length();
      camera.position.x = radius * Math.sin(rotationY) * Math.cos(rotationX);
      camera.position.y = radius * Math.sin(rotationX);
      camera.position.z = radius * Math.cos(rotationY) * Math.cos(rotationX);
      camera.lookAt(0, 0, 0);

      // Animate centroids with a subtle pulse
      centroidsGroup.children.forEach((child: any, index: number) => {
        if (index % 2 === 0) { // Only animate the main centroid spheres
          const scale = 1 + 0.1 * Math.sin(Date.now() * 0.003 + index);
          child.scale.setScalar(scale);
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      if (!mountRef.current) return;
      camera.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('mousedown', handleMouseDown);
      renderer.domElement.removeEventListener('mouseup', handleMouseUp);
      renderer.domElement.removeEventListener('mousemove', handleMouseMove);
      renderer.domElement.removeEventListener('wheel', handleWheel);
      
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [dataPoints, centroids]);

  if (!dataPoints.length) {
    return (
      <div style={{ 
        width: '100%', 
        height: 340, 
        background: '#111', 
        border: '1px solid rgba(255,255,255,0.08)', 
        borderRadius: 12,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'rgba(255,255,255,0.6)'
      }}>
        Loading 3D Plot...
      </div>
    );
  }

  return (
    <div>
      <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>3D Clustering Visualization</div>
      <div 
        ref={mountRef} 
        style={{ 
          width: '100%', 
          height: 340, 
          border: '1px solid rgba(255,255,255,0.08)', 
          borderRadius: 12,
          cursor: 'grab'
        }} 
      />
      <div style={{ marginTop: 8, fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
        Mouse: Rotate • Scroll: Zoom • Data points colored by nearest centroid
      </div>
    </div>
  );
}

export function CreatorFundTab() {
  const [categories, setCategories] = useState<Category[]>([])
  const [amount, setAmount] = useState<string>('100000')
  const [clusteringData, setClusteringData] = useState<ClusteringData>({ dataPoints: [], centroids: [] })

  useEffect(() => {
    mockApiService.getVideoCategories().then(setCategories)
    clusteringApiService.getClusteringData().then(setClusteringData)
  }, [])

  const total = useMemo(() => Number(amount || 0), [amount])

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 16, color: '#fff', fontFamily: 'sans-serif', padding: 20, background: '#000' }}>
      <div>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Fund Allocation Controls</div>
        <div style={{ background: '#121212', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 12, padding: 12 }}>
          <label style={{ display: 'block', color: 'rgba(255,255,255,0.8)', marginBottom: 8 }}>
            Total Fund Amount ($)
          </label>
          <input
            value={amount}
            onChange={e => setAmount(e.target.value)}
            placeholder="100000"
            style={{
              width: '100%',
              padding: '8px 10px',
              borderRadius: 8,
              border: '1px solid rgba(255,255,255,0.2)',
              background: '#0f0f0f',
              color: '#fff',
              boxSizing: 'border-box'
            }}
          />
          <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
            <button
              onClick={() => setAmount('100000')}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)', background: 'transparent', color: '#fff', cursor: 'pointer' }}
            >
              Quick: 100k
            </button>
            <button
              onClick={() => setAmount('250000')}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)', background: 'transparent', color: '#fff', cursor: 'pointer' }}
            >
              Quick: 250k
            </button>
          </div>
        </div>

        {/* Clustering Controls */}
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Clustering Controls</div>
          <div style={{ background: '#121212', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 12, padding: 12 }}>
            <button
              onClick={() => clusteringApiService.getClusteringData().then(setClusteringData)}
              style={{ 
                width: '100%',
                padding: '8px 12px', 
                borderRadius: 8, 
                border: '1px solid rgba(255,255,255,0.2)', 
                background: '#FE2C55', 
                color: '#fff', 
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              Refresh Clustering Data
            </button>
            <div style={{ marginTop: 8, fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
              Data Points: {clusteringData.dataPoints.length} | Centroids: {clusteringData.centroids.length}
            </div>
          </div>
        </div>
      </div>

      <div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16, marginBottom: 16 }}>
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

        {/* 3D Clustering Plot */}
        <div>
          <ThreeJSClusterPlot 
            dataPoints={clusteringData.dataPoints} 
            centroids={clusteringData.centroids} 
          />
        </div>
      </div>
    </div>
  )
}

function PieChart(props: { categories: Category[] }) {
  const { categories } = props;
  const total = categories.reduce((sum, c) => sum + c.popularityPercentage, 0);
  let cumulative = 0;
  
  const width = 340;
  const height = 340;
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) / 2 - 20;

  const colors = [
    '#FE2C55', '#25F4EE', '#F7B500', '#A450E6', '#40D8A0', 
    '#FF69B4', '#58A6FF', '#FF8C00', '#ADFF2F', '#DA70D6', 
    '#00CED1', '#FF4500'
  ];

  return (
    <div>
      <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Category Distribution</div>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ background: '#111', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }}>
        {categories.map((c, idx) => {
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
    </div>
  );
}