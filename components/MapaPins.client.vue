<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

interface CidadeCoords {
  lat: number
  lng: number
  nome: string
}

const props = defineProps<{
  corridasStats: Record<string, number>
  cidade?: CidadeCoords
}>()

const config = useRuntimeConfig()
const mapRef = ref<HTMLDivElement>()
const mapLoaded = ref(false)

let map: any = null

// Coordenadas padrão (Curvelo) ou da cidade selecionada
const cidadeCoords = computed(() => props.cidade || { lat: -18.7569, lng: -44.4308, nome: 'Curvelo' })

const statusColors: Record<string, string> = {
  'P': '#facc15',
  'F': '#22c55e',
  'A': '#10b981',
  'C': '#ef4444',
  'N': '#f97316',
  'S': '#3b82f6',
}

const statusLabels: Record<string, string> = {
  'P': 'Pendente',
  'F': 'Finalizada',
  'A': 'Aceita',
  'C': 'Cancelada',
  'N': 'Não Atendida',
  'S': 'Em Espera',
}

const total = computed(() => Object.values(props.corridasStats).reduce((a, b) => a + b, 0))

// Gerar GeoJSON com pontos para cada corrida
function generateGeoJSON() {
  const features: any[] = []
  
  Object.entries(props.corridasStats).forEach(([status, count]) => {
    for (let i = 0; i < Math.min(count, 50); i++) { // Limitar a 50 por status
      features.push({
        type: 'Feature',
        properties: { status, label: statusLabels[status], color: statusColors[status] },
        geometry: {
          type: 'Point',
          coordinates: [
            cidadeCoords.value.lng + (Math.random() - 0.5) * 0.08,
            cidadeCoords.value.lat + (Math.random() - 0.5) * 0.06
          ]
        }
      })
    }
  })
  
  return { type: 'FeatureCollection', features }
}

onMounted(async () => {
  await new Promise(r => setTimeout(r, 50))
  if (!mapRef.value) return

  const token = config.public.mapboxToken
  if (!token) return

  const mapboxgl = (await import('mapbox-gl')).default
  mapboxgl.accessToken = token as string

  map = new mapboxgl.Map({
    container: mapRef.value,
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [cidadeCoords.value.lng, cidadeCoords.value.lat],
    zoom: 13,
    attributionControl: false
  })

  map.on('load', () => {
    // Ocultar logo
    document.querySelectorAll('.mapboxgl-ctrl-logo, .mapboxgl-ctrl-attrib').forEach(el => {
      (el as HTMLElement).style.display = 'none'
    })

    // Adicionar source GeoJSON
    map.addSource('corridas', {
      type: 'geojson',
      data: generateGeoJSON()
    })

    // Adicionar layer de círculos (muito mais performático que markers DOM)
    Object.entries(statusColors).forEach(([status, color]) => {
      map.addLayer({
        id: `pins-${status}`,
        type: 'circle',
        source: 'corridas',
        filter: ['==', ['get', 'status'], status],
        paint: {
          'circle-radius': 6,
          'circle-color': color,
          'circle-stroke-width': 1,
          'circle-stroke-color': 'rgba(255,255,255,0.5)'
        }
      })
    })

    map.addControl(new mapboxgl.NavigationControl(), 'top-right')
    mapLoaded.value = true
  })
})

// Atualizar mapa quando os dados mudarem
watch(() => props.corridasStats, (newStats) => {
  if (map && mapLoaded.value && map.getSource('corridas')) {
    map.getSource('corridas').setData(generateGeoJSON())
  }
}, { deep: true })

// Atualizar mapa quando a cidade mudar
watch(() => props.cidade, (newCidade) => {
  if (map && mapLoaded.value && newCidade) {
    map.flyTo({
      center: [newCidade.lng, newCidade.lat],
      zoom: 13,
      duration: 1500
    })
    // Atualizar pontos para nova localização
    if (map.getSource('corridas')) {
      map.getSource('corridas').setData(generateGeoJSON())
    }
  }
}, { deep: true })

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div class="map-wrap">
    <div ref="mapRef" class="map-container"></div>
    
    <div class="map-badge">
      <span>📍</span>
      <div>
        <strong>Últimos 15 min</strong>
        <small>{{ total }} corridas no mapa</small>
      </div>
    </div>
    
    <div class="map-legend">
      <div class="legend-title">Legenda</div>
      <div v-for="(color, status) in statusColors" :key="status" class="legend-item">
        <span class="legend-dot" :style="{ background: color }"></span>
        <span>{{ statusLabels[status] }}: {{ corridasStats[status] || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-wrap {
  position: relative;
  height: 450px;
  border-radius: 12px;
  overflow: hidden;
  background: #1a1d23;
}
.map-container {
  width: 100%;
  height: 100%;
}
.map-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(26,29,35,0.95);
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #00C885;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1;
}
.map-badge strong {
  display: block;
  color: #00C885;
  font-size: 13px;
}
.map-badge small {
  color: #9ca3af;
  font-size: 10px;
}
.map-legend {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(26,29,35,0.95);
  padding: 10px;
  border-radius: 6px;
  z-index: 1;
  font-size: 11px;
}
.legend-title {
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 6px;
  text-transform: uppercase;
  font-size: 9px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #d1d5db;
  margin-bottom: 3px;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
</style>
